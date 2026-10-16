"""Shared policy runner for all datasets."""

from __future__ import annotations

import argparse
import asyncio
import glob
import importlib
import json
import os
from typing import Any, List, Optional

from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from aspec.meta.optimizer import Optimizer
from experiments.lib.llm import API_DEFAULTS, create_llm_config
from aspec.meta.dataset_registry import REGISTRY

API_TYPE_CHOICES = tuple(API_DEFAULTS)


def get_operator_names(registry_path: str) -> List[str]:
    """Dynamically import operator names from a registry module."""
    mod = importlib.import_module(registry_path)
    return mod.operator_names


def find_best_round_weights(dataset: str, sample: int, optimized_path: str) -> Optional[str]:
    """Find the weights file from the best performing round.

    Checks for a ``*_best_score_metadata.json`` first, then falls back to
    the file with the highest ``problemN`` suffix.
    """
    train_dir = os.path.join(optimized_path, dataset, "train")

    metadata_path = os.path.join(train_dir, f"{dataset}_controller_sample{sample}_best_score_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            checkpoint_path = metadata.get("checkpoint_path")
            best_score = metadata.get("best_score", 0.0)
            if checkpoint_path and os.path.exists(checkpoint_path):
                logger.info(f"Found best score checkpoint: {checkpoint_path} (score: {best_score:.4f})")
                return checkpoint_path
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load best score metadata: {e}")

    pattern = f"{dataset}_controller_sample{sample}*problem*.pth"
    weight_files = glob.glob(os.path.join(train_dir, pattern))
    if not weight_files:
        logger.warning(f"No weight files found matching pattern: {pattern}")
        return None

    best_file = None
    best_problem_count = 0
    for weight_file in weight_files:
        filename = os.path.basename(weight_file)
        try:
            problem_count = int(filename.split("problem")[1].split(".")[0])
            if problem_count > best_problem_count:
                best_problem_count = problem_count
                best_file = weight_file
        except (IndexError, ValueError):
            continue

    if best_file:
        logger.info(f"Found best round weights: {best_file} (problem {best_problem_count})")
        return best_file
    logger.warning("Could not determine best round weights")
    return None


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------


async def run_policy(
    dataset: str,
    split: str = "train",
    model: str = "gemini-2.0-flash",
    api_type: str = "gemini",
    sample: int = 2,
    round: int = 1,
    lr: float = 1e-4,
    batch_size: int = 4,
    optimized_path: str = "experiments/datasets",
    preloaded_weights_path: Optional[str] = None,
    max_specialist_pool: Optional[int] = None,
    operators: Optional[List[str]] = None,
) -> dict[str, Any]:
    """Run the ASPEC optimizer for any dataset.

    This replaces the per-dataset run_*_policy.py / train_*_policy.py /
    eval_*_policy.py scripts.
    """
    cfg = REGISTRY.get(dataset)
    if cfg is None:
        raise ValueError(f"Unknown dataset: {dataset}. Available: {sorted(REGISTRY)}")

    # Resolve operators
    if operators is None:
        operators = get_operator_names(cfg.operator_registry)

    # Resolve weights
    if preloaded_weights_path is None:
        preloaded_weights_path = cfg.default_weights

    opt_llm_config = create_llm_config(model, api_type=api_type)
    exec_llm_config = create_llm_config(model, api_type=api_type)

    logger.info(f"Starting optimizer {split}ing for {dataset}")
    logger.info(f"Operators: {operators}")
    logger.info(f"Learning rate: {lr}")

    kwargs: dict[str, Any] = dict(
        dataset=dataset,
        question_type=cfg.question_type,
        opt_llm_config=opt_llm_config,
        exec_llm_config=exec_llm_config,
        operators=operators,
        sample=sample,
        optimized_path=optimized_path,
        round=round,
        lr=lr,
        preloaded_weights_path=preloaded_weights_path,
        batch_size=batch_size,
        is_test=(split == "test"),
        dataset_split=split,
    )
    if max_specialist_pool is not None:
        kwargs["max_specialized_operators"] = max_specialist_pool
    elif cfg.max_specialist_pool != 5:
        kwargs["max_specialized_operators"] = cfg.max_specialist_pool

    # Merge dataset-specific kwargs
    kwargs.update(cfg.extra_optimizer_kwargs)

    optimizer = Optimizer(**kwargs)
    score = await optimizer.optimize(mode="Graph")

    if score is not None:
        logger.info(f"Completed. Final score: {score:.4f}")
    else:
        logger.info("Completed. Final score: None")

    return {"score": score, "dataset": dataset, "operators": operators}


async def train_multi_round(
    dataset: str,
    max_rounds: int = 1,
    model: str = "gemini-2.0-flash",
    api_type: str = "gemini",
    sample: int = 2,
    lr: float = 1e-4,
    batch_size: int = 4,
    optimized_path: str = "experiments/datasets",
    operators: Optional[List[str]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run multiple training rounds, tracking the best score."""
    cfg = REGISTRY.get(dataset)
    if cfg is None:
        raise ValueError(f"Unknown dataset: {dataset}. Available: {sorted(REGISTRY)}")

    if operators is None:
        operators = get_operator_names(cfg.operator_registry)

    logger.info(f"Training on {dataset} for {max_rounds} rounds")

    best_score = 0.0
    best_round = 0
    round_scores: dict[int, Optional[float]] = {}

    for round_num in range(1, max_rounds + 1):
        logger.info(f"\n--- Training Round {round_num}/{max_rounds} ---")
        try:
            result = await run_policy(
                dataset=dataset,
                split="train",
                model=model,
                sample=sample,
                round=round_num,
                lr=lr,
                batch_size=batch_size,
                optimized_path=optimized_path,
                api_type=api_type,
                operators=operators,
                **kwargs,
            )
            score = result["score"]
            round_scores[round_num] = score
            if score is not None and score > best_score:
                best_score = score
                best_round = round_num
                logger.info(f"New best score! Round {round_num}: {score:.4f}")
        except Exception as e:
            logger.error(f"Error in training round {round_num}: {e}")
            round_scores[round_num] = None

    logger.warning("\n=== Training complete ===")
    logger.warning(f"Best score achieved: {best_score:.4f} in round {best_round}")
    logger.warning(f"All round scores: {round_scores}")

    return {
        "best_score": best_score,
        "best_round": best_round,
        "round_scores": round_scores,
        "dataset": dataset,
        "operators": operators,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run ASPEC policy optimizer on any dataset")
    p.add_argument(
        "--dataset",
        required=True,
        choices=sorted(REGISTRY),
        help="Dataset to run on",
    )
    p.add_argument("--split", default="train", choices=["train", "test"])
    p.add_argument("--model", default="gemini-2.0-flash")
    p.add_argument("--api-type", choices=API_TYPE_CHOICES, default="gemini")
    p.add_argument("--sample", type=int, default=2)
    p.add_argument("--round", type=int, default=1)
    p.add_argument(
        "--train_rounds", type=int, default=None, help="Multi-round training: run N rounds tracking best score"
    )
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--batch_size", type=int, default=4)
    p.add_argument("--optimized_path", default="experiments/datasets")
    p.add_argument("--preloaded_weights_path", default=None)
    p.add_argument("--max_specialist_pool", type=int, default=None)
    return p


def main() -> None:
    args = build_parser().parse_args()

    if args.train_rounds is not None:
        asyncio.run(
            train_multi_round(
                dataset=args.dataset,
                max_rounds=args.train_rounds,
                model=args.model,
                api_type=args.api_type,
                sample=args.sample,
                lr=args.lr,
                batch_size=args.batch_size,
                optimized_path=args.optimized_path,
            )
        )
    else:
        asyncio.run(
            run_policy(
                dataset=args.dataset,
                split=args.split,
                model=args.model,
                api_type=args.api_type,
                sample=args.sample,
                round=args.round,
                lr=args.lr,
                batch_size=args.batch_size,
                optimized_path=args.optimized_path,
                preloaded_weights_path=args.preloaded_weights_path,
                max_specialist_pool=args.max_specialist_pool,
            )
        )


if __name__ == "__main__":
    main()
