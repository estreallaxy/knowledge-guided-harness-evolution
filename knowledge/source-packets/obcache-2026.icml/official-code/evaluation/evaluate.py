# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import random
import sys
from contextlib import nullcontext
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import torch
import yaml

CURRENT_DIR = Path(__file__).resolve().parent
OBCACHE_ROOT = CURRENT_DIR.parent
for path in (str(OBCACHE_ROOT), str(CURRENT_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from datasets import load_dataset
from evaluate_registry import DATASET_REGISTRY, PRESS_REGISTRY, SCORER_REGISTRY
from fire import Fire
from tqdm import tqdm
from transformers import DynamicCache, FineGrainedFP8Config, Pipeline, pipeline

from kvpress import ScorerPress

logger = logging.getLogger(__name__)

LONGBENCH_NO_CHAT_TEMPLATE_TASKS = {"trec", "triviaqa", "samsum", "lsht", "lcc", "repobench-p"}

try:
    import wandb
except ImportError:
    wandb = None


@dataclass
class EvaluationConfig:
    """Dataclass to handle all the configuration for the evaluation."""

    # Core evaluation parameters
    dataset: str = "ruler"
    data_dir: Optional[str] = None
    model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    model_path: Optional[str] = None
    device: Optional[str] = None
    press_name: str = "no_press"
    compression_ratio: float = 1.0
    key_channel_compression_ratio: Optional[float] = None
    threshold: Optional[float] = None

    # Dataset and generation parameters
    fraction: float = 1.0
    max_new_tokens: Optional[int] = None
    max_context_length: Optional[int] = None
    query_aware: bool = False

    # Decoding parameters
    compression_interval: Optional[int] = None
    target_size: Optional[int] = None
    hidden_states_buffer_size: Optional[int] = None

    # Output and logging
    output_dir: str = "./results"
    log_level: str = "INFO"
    wandb: bool = False
    wandb_project: str = "kvpress-eval"
    wandb_entity: Optional[str] = None
    wandb_run_name: Optional[str] = None

    # Model-specific parameters
    model_kwargs: Optional[Dict[str, Any]] = None

    # Press information (will be set after press setup)
    press_init_command: Optional[str] = None

    # For reproducibility
    seed: int = 42

    # Quantization
    fp8: bool = False

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate dataset
        assert self.dataset in DATASET_REGISTRY, f"No dataset found for {self.dataset}"
        assert self.dataset in SCORER_REGISTRY, f"No scorer found for {self.dataset}"

        # Validate press
        assert self.press_name in PRESS_REGISTRY, f"Press '{self.press_name}' not found in PRESS_REGISTRY"

        if self.press_name == "no_press":
            # override compression_ratio to 0.0
            logger.info("Using 'no_press' configuration. Overriding compression_ratio to 0.0")
            self.compression_ratio = 0.0

        # Only validate key_channel_compression_ratio if it's not None
        if self.key_channel_compression_ratio is not None:
            assert (
                0.0 <= self.key_channel_compression_ratio <= 1.0
            ), f"key_channel_compression_ratio must be between 0.0 and 1.0, got {self.key_channel_compression_ratio}"

        # Validate fraction
        assert 0.0 < self.fraction <= 1.0, f"fraction must be between 0.0 and 1.0, got {self.fraction}"

        # Initialize model_kwargs if None
        if self.model_kwargs is None:
            self.model_kwargs = {}

        if self.model_path is not None:
            model_path = Path(self.model_path).expanduser()
            assert model_path.exists(), f"Local model path does not exist: {model_path}"
            assert model_path.is_dir(), f"Local model path must be a directory: {model_path}"
            self.model_path = str(model_path.resolve())

    def get_results_dir(self, output_dir: Path) -> Path:
        """
        Generates the unique save directory and filenames based on configuration parameters.

        Parameters
        ----------
        output_dir : Path
            The output directory path

        Returns
        -------
        Path
            The path to the results directory
        """
        # Build directory name components
        components = [
            self.dataset,
            str(self.data_dir) if self.data_dir else "",
            self.get_model_identifier().replace("/", "--"),
            self.press_name,
            f"{self.compression_ratio:.2f}",
        ]

        if self.threshold is not None:
            components[-1] = f"{self.threshold:.2f}"
        if self.fraction < 1.0:
            components.append(f"fraction{self.fraction:.3f}")
        if self.max_context_length is not None:
            components.append(f"max_context{self.max_context_length}")
        if self.query_aware:
            components.append("query_aware")
        if self.key_channel_compression_ratio is not None:
            components.append(f"key_channel_cr{self.key_channel_compression_ratio:.2f}")
        dir_name = "__".join(filter(None, components))  # Filter None/empty strings
        config_dir = output_dir / dir_name

        # Make sure the directory does not exist, if it does, add a number to the end
        # This is to avoid overwriting results
        if config_dir.exists():
            i = 1
            while (config_dir / f"{i}").exists():
                i += 1
            config_dir = config_dir / f"{i}"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def get_model_source(self) -> str:
        """Return the model source passed to transformers."""
        return self.model_path or self.model

    def get_model_identifier(self) -> str:
        """Return a compact identifier for filenames and logs."""
        if self.model_path is None:
            return self.model
        resolved_path = Path(self.model_path)
        return f"local--{resolved_path.name}"

    def save_config(self, config_filename: Path):
        """
        Saves the evaluation configuration to a YAML file.
        """
        with open(str(config_filename), "w") as f:
            yaml.dump(asdict(self), f, default_flow_style=False, indent=2, sort_keys=False)


def _load_yaml_config(path: str | Path) -> dict:
    """Loads a YAML file. Returns an empty dict if it doesn't exist."""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning(f"Config file not found at {path}. Using only command-line arguments and defaults.")
        return {}


def _coerce_bool_config_values(config: dict) -> dict:
    """Normalize boolean strings from Fire/YAML before constructing EvaluationConfig."""
    bool_fields = ("query_aware", "wandb", "fp8")
    for field_name in bool_fields:
        value = config.get(field_name)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "y"}:
                config[field_name] = True
            elif normalized in {"false", "0", "no", "n"}:
                config[field_name] = False
    return config


class EvaluationRunner:
    """
    EvaluationRunner class that orchestrates the entire evaluation process.

    Parameters
    ----------
    config : EvaluationConfig
        The configuration for the evaluation run.

    The final output will be predictions_<config>.csv and metrics_<config>.json in the output_dir.
    If the evaluation files already exist, evaluation will be skipped.

    """

    def __init__(self, config: EvaluationConfig):
        """
        Initializes the EvaluationRunner with a given configuration.

        Parameters
        ----------
        config : EvaluationConfig
            The configuration for the evaluation run.
        """
        self.config = config
        self.pipeline: Optional[Pipeline] = None  # Will be set by _setup_model_pipeline()
        self.press: None | ScorerPress = None  # Will be set by _setup_press()
        self.df: Optional[pd.DataFrame] = None  # Will be set by _load_dataset()
        self._wandb_run = None
        self._setup_logging()
        self._setup_deterministic_seeds()
        logger.info(f"Initialized EvaluationRunner with config:\n{json.dumps(asdict(self.config), indent=2)}")

    def _setup_deterministic_seeds(self):
        """Set deterministic seeds for reproducible results."""
        torch.manual_seed(self.config.seed)
        np.random.seed(self.config.seed)
        random.seed(self.config.seed)

        if torch.cuda.is_available():
            torch.cuda.manual_seed(self.config.seed)
            torch.cuda.manual_seed_all(self.config.seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        logger.info(f"Set deterministic seeds to {self.config.seed}")

    def _setup_logging(self):
        """Configures the logging level based on the config."""
        log_level = self.config.log_level.upper()

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(log_level)

    def _setup_directories(self) -> Path:
        """
        Creates the output directory for saving results if it doesn't exist.

        Returns
        -------
        Path
            The path to the output directory.
        """
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory set to: {output_dir}")
        return output_dir

    def _init_wandb(self, results_dir: Path):
        if not self.config.wandb:
            return
        if wandb is None:
            raise ImportError("wandb is not installed. Install it or disable the wandb flag.")

        if results_dir.name.isdigit():
            run_name = results_dir.parent.name + f"_{results_dir.name}"
        else:
            run_name = results_dir.name
        self._wandb_run = wandb.init(
            project=self.config.wandb_project,
            entity=self.config.wandb_entity,
            name=run_name,
            config={
                "dataset": self.config.dataset,
                "data_dir": self.config.data_dir,
                "model": self.config.get_model_identifier(),
                "press_name": self.config.press_name,
                "compression_ratio": self.config.compression_ratio,
                "query_aware": self.config.query_aware,
                "max_context_length": self.config.max_context_length,
                "output_dir": self.config.output_dir,
                "results_dir": str(results_dir),
                "device": self.config.device,
            },
            job_type="evaluation",
            reinit=True,
        )
        if self._wandb_run is not None:
            self._wandb_run.summary["status"] = "running"
            self._wandb_run.summary["results_dir"] = str(results_dir)

    def _wandb_log_progress(self, completed: int, total: int):
        if self._wandb_run is None:
            return
        self._wandb_run.log(
            {
                "progress/completed": completed,
                "progress/total": total,
                "progress/fraction": completed / total if total > 0 else 0.0,
            }
        )

    def _wandb_finish_success(self, metrics_path: Path):
        if self._wandb_run is None:
            return

        summary = {
            "status": "completed",
            "metrics_path": str(metrics_path),
        }
        try:
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
            task_scores = []
            for task_name, task_metrics in metrics.items():
                if isinstance(task_metrics, dict):
                    for metric_name, value in task_metrics.items():
                        if isinstance(value, (int, float)):
                            summary[f"metrics/{task_name}/{metric_name}"] = value
                            if metric_name == "string_match":
                                task_scores.append(float(value))
            if task_scores:
                summary["metrics/avg_string_match"] = sum(task_scores) / len(task_scores)
        except Exception as exc:
            logger.warning(f"Failed to load metrics for wandb summary: {exc}")

        for key, value in summary.items():
            self._wandb_run.summary[key] = value
        self._wandb_run.finish()
        self._wandb_run = None

    def _wandb_finish_failure(self, exc: Exception):
        if self._wandb_run is None:
            return
        self._wandb_run.summary["status"] = "failed"
        self._wandb_run.summary["error"] = str(exc)
        self._wandb_run.finish(exit_code=1)
        self._wandb_run = None

    def _setup_press(self):
        """
        Initializes the KVPress instance and applies compression ratios based on its type.
        """
        press_name = self.config.press_name
        compression_ratio = self.config.compression_ratio

        press = PRESS_REGISTRY[press_name]

        if hasattr(press, "compression_ratio"):
            press.compression_ratio = compression_ratio
            logger.info(f"Set {press.__class__.__name__} compression_ratio to {compression_ratio}")
        elif press is not None:
            logger.warning(
                f"Press {press.__class__.__name__} has no 'compression_ratio' attribute. This is expected if you set `no_press`."
            )

        self.press = press
        # Set the press info in the config for saving to YAML
        self.config.press_init_command = str(press)
        logger.info(f"KV Press '{press_name}' setup.")

    def _load_and_prepare_dataset(self):
        """
        Loads the dataset specified in the config and applies sampling/filtering.
        """
        dataset_name = self.config.dataset
        data_dir = str(self.config.data_dir) if self.config.data_dir else None
        fraction = self.config.fraction

        logger.info(f"Loading dataset: {DATASET_REGISTRY[dataset_name]} (data_dir: {data_dir})")
        df = load_dataset(DATASET_REGISTRY[dataset_name], data_dir=data_dir, split="test").to_pandas()

        if fraction < 1.0:
            original_len = len(df)
            df = df.sample(frac=fraction, random_state=self.config.seed)
            logger.info(f"Sampled {len(df)} samples ({fraction:.2f}) from original {original_len} samples.")

        logger.info(f"Dataset loaded with {len(df)} entries.")

        if self.config.query_aware:
            logger.info("Query-aware compression: including question in context for compression.")
            df["context"] = df["context"] + df["question"]  # type: ignore[index]
            df["question"] = ""  # type: ignore[index]

        self.df = df
        logger.info(f"Dataset processed with {len(self.df)} entries.")

    def _use_chat_template_for_rows(self, rows: pd.DataFrame | pd.Series) -> bool:
        if self.config.dataset not in {"longbench", "longbench-e"}:
            return True
        task = rows["task"].iloc[0] if isinstance(rows, pd.DataFrame) and "task" in rows else rows.get("task")
        task = str(task or self.config.data_dir or "").removesuffix("_e").removesuffix("-e")
        return task not in LONGBENCH_NO_CHAT_TEMPLATE_TASKS

    def _setup_model_pipeline(self):
        model_source = self.config.get_model_source()
        device = self.config.device

        if device is None:
            device = "auto" if torch.cuda.is_available() else "cpu"
            logger.info(f"No device specified, auto-detected device: {device}")

        model_kwargs = self.config.model_kwargs or {}

        if self.config.fp8:
            model_kwargs["quantization_config"] = FineGrainedFP8Config()
            logger.info("FP8 quantization enabled.")

        try:
            import flash_attn  # noqa: F401

            model_kwargs["attn_implementation"] = "flash_attention_2"
            logger.info("Flash Attention 2 detected, setting attn_implementation to 'flash_attention_2'.")
        except ImportError:
            logger.info("Flash Attention 2 not available, using default attn_implementation.")
            pass

        logger.info(
            f"Loading model pipeline for: {model_source} on device: {device} with model_kwargs: {model_kwargs}"
        )
        pipeline_kwargs = {
            "model": model_source,
            "model_kwargs": model_kwargs,
            "trust_remote_code": True,
        }
        if self.config.model_path is not None:
            pipeline_kwargs["local_files_only"] = True
        if device == "auto":
            pipeline_kwargs["device_map"] = "auto"
        else:
            pipeline_kwargs["device"] = device
        self.pipeline = pipeline("kv-press-text-generation", **pipeline_kwargs)

        self.pipeline.model.eval()
        logger.info("Model pipeline loaded.")
        logger.info(f"Model dtype: {self.pipeline.model.dtype}")

    @torch.inference_mode()
    def _run_inference(self, predictions_filename: Path):
        """
        Executes the inference process on the prepared dataset using the model pipeline.
        """

        self.df["predicted_answer"] = None  # type: ignore[index]
        self._save_results(predictions_filename)

        df_context_grouped = self.df.groupby("context", sort=False)  # type: ignore[union-attr]
        assert all(
            df_context_grouped["answer_prefix"].nunique() == 1
        ), "Inconsistent 'answer_prefix' within the same context group detected."

        logger.info("Starting inference...")
        total = int(self.df["context"].nunique())  # type: ignore[union-attr]
        for completed, (context, df_group) in enumerate(
            tqdm(df_context_grouped, total=total, desc="Running Inference"), start=1
        ):  # type: ignore[union-attr]
            questions = df_group["question"].to_list()
            max_new_tokens = self.config.max_new_tokens or df_group["max_new_tokens"].iloc[0]
            answer_prefix = df_group["answer_prefix"].iloc[0]
            input_tensors = self.pipeline.preprocess(  # type: ignore[union-attr]
                context=context,
                questions=questions,
                answer_prefix=answer_prefix,
                max_context_length=(
                    self.config.max_context_length
                    if self.config.max_context_length is not None
                    else min(self.pipeline.tokenizer.model_max_length, int(1e10))  # type: ignore[union-attr]
                ),
                use_chat_template=self._use_chat_template_for_rows(df_group),
            )
            context_ids = input_tensors["context_ids"].to(self.pipeline.model.device)  # type: ignore[union-attr]
            context_length = context_ids.shape[1]
            cache = DynamicCache()

            with self.press(self.pipeline.model) if self.press is not None else nullcontext():  # type: ignore[misc]
                self.pipeline.model.model(input_ids=context_ids, past_key_values=cache)  # type: ignore[union-attr]

            for row_index, question_ids in zip(df_group.index, input_tensors["questions_ids"]):
                cache_seq_lengths = [cache.get_seq_length(layer_idx) for layer_idx in range(len(cache))]
                answer = self.pipeline.generate_answer(  # type: ignore[union-attr]
                    question_ids=question_ids.to(self.pipeline.model.device),  # type: ignore[union-attr]
                    cache=cache,
                    context_length=context_length,
                    max_new_tokens=max_new_tokens,
                )
                self.pipeline._remove_answer_from_cache(cache, cache_seq_lengths)  # type: ignore[union-attr]

                self.df.loc[row_index, "predicted_answer"] = answer  # type: ignore[union-attr]
                self.df.loc[row_index, "compression_ratio"] = (
                    self.press.compression_ratio if self.press is not None else 0.0  # type: ignore[attr-defined]
                )  # type: ignore[union-attr, attr-defined]
                self._save_results(predictions_filename)
            self._wandb_log_progress(completed, total)
            torch.cuda.empty_cache()

        logger.info("Inference completed.")

    def _prediction_columns(self) -> list[str]:
        return [column for column in self.df.columns if column != "context"]  # type: ignore[union-attr]

    def _write_predictions_csv(self, save_filename: Path):
        tmp_filename = save_filename.with_name(f"{save_filename.name}.tmp")
        with open(tmp_filename, "w", newline="") as handle:
            self.df[self._prediction_columns()].to_csv(handle, index=False)  # type: ignore[index]
            handle.flush()
            os.fsync(handle.fileno())
        tmp_filename.replace(save_filename)

    def _save_results(self, save_filename: Path):
        """
        Saves the predicted answers and compression ratios to a CSV file.

        Parameters
        ----------
        save_filename : Path
            The full path including filename to save the CSV.
        """
        self._write_predictions_csv(save_filename)
        logger.info(f"Results saved to {save_filename}")

    def _calculate_and_save_metrics(self, save_filename: Path):
        """
        Calculates evaluation metrics and saves them to a JSON file.

        Parameters
        ----------
        save_filename : Path
            The base filename (e.g., CSV path) to derive the JSON path from.
        """
        dataset_name = self.config.dataset
        scorer = SCORER_REGISTRY[dataset_name]

        logger.info(f"Calculating metrics for dataset: {dataset_name}")
        metrics = scorer(self.df)  # type: ignore[call-arg]

        with open(str(save_filename), "w") as f:
            json.dump(metrics, f, indent=4)  # Pretty print JSON

        logger.info(f"Metrics saved to {save_filename}")
        logger.info(f"Metrics:\n{json.dumps(metrics, indent=2)}")

    def run_evaluation(self):
        """
        Orchestrates the entire evaluation process.
        """
        logger.info("Starting evaluation run...")
        output_dir = self._setup_directories()

        results_dir = self.config.get_results_dir(output_dir)
        predictions_filename = results_dir / "predictions.csv"
        metrics_filename = results_dir / "metrics.json"
        config_filename = results_dir / "config.yaml"

        if predictions_filename.exists() and metrics_filename.exists():
            logger.info(
                f"Evaluation files already exist at \n {predictions_filename} \n {metrics_filename}.\nSkipping..."
            )
            return

        self._init_wandb(results_dir)

        try:
            self._setup_press()
            self._setup_model_pipeline()
            self._load_and_prepare_dataset()
            self.config.save_config(config_filename)

            self._run_inference(predictions_filename)
            self._save_results(predictions_filename)
            self._calculate_and_save_metrics(metrics_filename)
            self._wandb_finish_success(metrics_filename)
            logger.info("Evaluation run completed successfully.")
        except Exception as exc:
            self._wandb_finish_failure(exc)
            raise


# --- Command-Line Interface ---
class CliEntryPoint:
    """
    CLI entry point for building configuration and running the evaluation.

    This class provides a command-line interface for running KVPress evaluations.
    Configuration can be specified via:
    1. YAML config file (default: "./evaluate_config.yaml")
    2. Command-line arguments (highest priority)
    """

    def __call__(self, config_file: Optional[str] = "./evaluate_config.yaml", **cli_overrides):
        """
        Builds the configuration and runs the evaluation.

        Configuration is built by layering:
        1. Default values from EvaluationConfig
        2. Values from YAML config file
        3. Command-line arguments (highest priority)
        """
        # 1. Start with dataclass defaults.
        final_args = asdict(EvaluationConfig())

        # 2. Layer YAML values on top.
        yaml_config = _load_yaml_config(config_file)
        final_args.update(yaml_config)

        # 3. Layer CLI arguments on top (highest priority).
        # Filter out None values from CLI overrides
        cli_args = {k: v for k, v in cli_overrides.items() if v is not None}
        final_args.update(cli_args)
        final_args = _coerce_bool_config_values(final_args)

        # 4. Create and validate the final config object.
        try:
            config = EvaluationConfig(**final_args)
        except TypeError as e:
            # Provide a user-friendly error for bad arguments.
            print(f"Error: Invalid configuration argument provided. {e}", file=sys.stderr)
            sys.exit(1)

        runner = EvaluationRunner(config)
        runner.run_evaluation()


if __name__ == "__main__":
    Fire(CliEntryPoint)
