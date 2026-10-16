"""Unified ADAS runner for all datasets.

Usage:
    pixi run python -m experiments.scripts.eval_adas --dataset GPQA
    pixi run python -m experiments.scripts.eval_adas --dataset SciCode --n_generation 14
    pixi run python -m experiments.scripts.eval_adas --dataset MMLU --agent COT_SC --test_size 800
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from types import SimpleNamespace


def _run_gpqa(args: argparse.Namespace) -> None:
    sys.path.append(os.getcwd())
    sys.path.append(os.path.join(os.getcwd(), "ADAS/_gpqa"))

    from ADAS._gpqa import search as search_module
    from ADAS._gpqa.search import evaluate, search

    os.makedirs(args.save_dir, exist_ok=True)

    test_data_filename = args.data_filename

    # Search phase on train split
    print("======== STARTING SEARCH PHASE ========")
    args.data_filename = args.train_data_filename
    print(f"Starting search phase with: {args.data_filename}")
    search_module.SEARCHING_MODE = True
    asyncio.run(search(args))

    # Evaluation phase on test split
    print("\n======== STARTING EVALUATION PHASE ========")
    args.data_filename = test_data_filename
    print(f"Starting evaluation phase with: {args.data_filename}")
    search_module.SEARCHING_MODE = False
    asyncio.run(evaluate(args))


def _run_scicode(args: argparse.Namespace) -> None:
    sys.path.append(os.getcwd())
    sys.path.append(os.path.join(os.getcwd(), "ADAS/_scicode"))

    from ADAS._scicode.search import evaluate

    os.makedirs(args.save_dir, exist_ok=True)

    print("\n======== STARTING EVALUATION PHASE ========")
    evaluate(args)


def _run_mmlu(args: argparse.Namespace) -> None:
    from ADAS._mmlu import mmlu_prompt as adas_prompts
    from ADAS._mmlu import search as adas_search

    agent_name = (args.agent or "COT").strip().upper()
    mapping = {
        "COT": adas_prompts.COT["code"],
        "COT_SC": adas_prompts.COT_SC["code"],
        "REFLEXION": adas_prompts.Reflexion["code"],
        "LLM_DEBATE": adas_prompts.LLM_debate["code"],
        "STEP_BACK": adas_prompts.Take_a_step_back["code"],
        "QD": adas_prompts.QD["code"],
        "ROLE_ASSIGNMENT": adas_prompts.Role_Assignment["code"],
    }
    if agent_name not in mapping:
        raise ValueError(f"Unknown agent '{agent_name}'. Supported: {list(mapping.keys())}")

    forward_str = mapping[agent_name]

    eval_args = SimpleNamespace(
        data_filename=args.data_filename,
        valid_size=args.valid_size,
        test_size=args.test_size,
        shuffle_seed=args.shuffle_seed,
        n_repreat=args.n_repeat,
        multiprocessing=(not args.no_multiprocessing),
        max_workers=args.max_workers,
    )

    adas_search.SEARCHING_MODE = False
    adas_search.evaluate_forward_fn(eval_args, forward_str)


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified ADAS runner for all datasets.")
    parser.add_argument(
        "--dataset",
        required=True,
        choices=["GPQA", "SciCode", "MMLU"],
        help="Dataset to run ADAS on",
    )

    # Shared arguments
    parser.add_argument("--save_dir", default="results/")
    parser.add_argument("--model", default="gemini-2.0-flash", help="LLM model")
    parser.add_argument("--n_generation", type=int, default=5)
    parser.add_argument("--debug_max", type=int, default=3)
    parser.add_argument("--valid_size", type=int, default=32)

    # GPQA-specific
    parser.add_argument("--data_filename", default=None)
    parser.add_argument("--train_data_filename", default=None)
    parser.add_argument("--expr_name", default=None)
    parser.add_argument("--n_repreat", type=int, default=1)
    parser.add_argument("--per_task_timeout", type=int, default=60)
    parser.add_argument("--multiprocessing", action="store_true", default=False)
    parser.add_argument("--max_workers", type=int, default=1)

    # SciCode-specific
    parser.add_argument("--test_data_filename", default=None)
    parser.add_argument("--h5_path", default="data/scicode_test_data.h5")
    parser.add_argument("--exec_model", default="gemini-2.0-flash")

    # MMLU-specific
    parser.add_argument(
        "--agent", default="COT", help="ADAS agent: COT, COT_SC, REFLEXION, LLM_DEBATE, STEP_BACK, QD, ROLE_ASSIGNMENT"
    )
    parser.add_argument("--test_size", type=int, default=800)
    parser.add_argument("--shuffle_seed", type=int, default=0)
    parser.add_argument("--n_repeat", type=int, default=1)
    parser.add_argument("--no_multiprocessing", action="store_true")

    args = parser.parse_args()

    # Apply dataset-specific defaults
    if args.dataset == "GPQA":
        if args.data_filename is None:
            args.data_filename = "data/gpqa_test.jsonl"
        if args.train_data_filename is None:
            args.train_data_filename = "data/gpqa_train.jsonl"
        if args.expr_name is None:
            args.expr_name = "gpqa_adas"
        args.debug = True
        _run_gpqa(args)

    elif args.dataset == "SciCode":
        if args.data_filename is None:
            args.data_filename = "data/scicode_train.jsonl"
        if args.test_data_filename is None:
            args.test_data_filename = "data/scicode_test.jsonl"
        if args.expr_name is None:
            args.expr_name = "scicode_adas"
        if args.n_generation == 5:
            args.n_generation = 14  # SciCode default
        if args.valid_size == 32:
            args.valid_size = 16  # SciCode default
        if args.test_size == 800:
            args.test_size = -1  # SciCode default
        _run_scicode(args)

    elif args.dataset == "MMLU":
        if args.data_filename is None:
            args.data_filename = os.path.abspath(os.path.join("experiments", "datasets", "mmlu.csv"))
        _run_mmlu(args)


if __name__ == "__main__":
    main()
