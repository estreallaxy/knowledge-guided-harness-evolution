"""Centralized per-dataset configuration registry.

Eliminates scattered if/elif dataset dispatch chains across the codebase.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field


@dataclass
class DatasetSpec:
    """Configuration for a single benchmark dataset."""

    name: str
    question_type: str  # "math", "code", "qa", "physics"
    benchmark_module: str  # e.g. "aspec.benchmarks.math"
    benchmark_class: str  # e.g. "MATHBenchmark"
    workflow_pattern: str  # e.g. "experiments.datasets.{name}.{split}.graph"
    post_exec_prompt_module: str  # e.g. "experiments.datasets.{name}.train.template.op_prompt"
    data_file_pattern: str  # e.g. "data/math_{split}.jsonl"
    operator_registry: str  # dotted import path
    default_architecture: list[list[str]] = field(default_factory=lambda: [["CoT"], ["SelfRefine"]])
    semaphore_divisor: int = 1  # SciCode uses 2 (batch_size // 2)
    default_weights: str | None = None
    extra_optimizer_kwargs: dict = field(default_factory=dict)
    max_specialist_pool: int = 5


REGISTRY: dict[str, DatasetSpec] = {
    "MATH": DatasetSpec(
        name="MATH",
        question_type="code",
        benchmark_module="aspec.benchmarks.math",
        benchmark_class="MATHBenchmark",
        workflow_pattern="experiments.datasets.MATH.{split}.graph",
        post_exec_prompt_module="experiments.datasets.MATH.train.template.op_prompt",
        data_file_pattern="data/math_{split}.jsonl",
        operator_registry="experiments.datasets.MATH.train.template.operator_registry",
    ),
    "HumanEval": DatasetSpec(
        name="HumanEval",
        question_type="code",
        benchmark_module="aspec.benchmarks.humaneval",
        benchmark_class="HumanEvalBenchmark",
        workflow_pattern="experiments.datasets.HumanEval.{split}.graph",
        post_exec_prompt_module="experiments.datasets.HumanEval.train.template.op_prompt",
        data_file_pattern="data/humaneval_{split}.jsonl",
        operator_registry="experiments.datasets.HumanEval.train.template.operator_registry",
    ),
    "GPQA": DatasetSpec(
        name="GPQA",
        question_type="physics",
        benchmark_module="aspec.benchmarks.gpqa",
        benchmark_class="GPQABenchmark",
        workflow_pattern="experiments.datasets.GPQA.{split}.graph",
        post_exec_prompt_module="experiments.datasets.GPQA.train.template.op_prompt",
        data_file_pattern="data/gpqa_{split}.jsonl",
        operator_registry="experiments.datasets.GPQA.train.template.operator_registry",
    ),
    "MMLU": DatasetSpec(
        name="MMLU",
        question_type="qa",
        benchmark_module="aspec.benchmarks.mmlu",
        benchmark_class="MMLUBenchmark",
        workflow_pattern="experiments.datasets.MMLU.{split}.graph",
        post_exec_prompt_module="experiments.datasets.MMLU.train.template.op_prompt",
        data_file_pattern="data/mmlu_{split}.jsonl",
        operator_registry="experiments.datasets.MMLU.test.template.operator_registry",
    ),
    "SciCode": DatasetSpec(
        name="SciCode",
        question_type="code",
        benchmark_module="aspec.benchmarks.scicode",
        benchmark_class="ScicodeBenchmark",
        workflow_pattern="experiments.datasets.SciCode.{split}.graph",
        post_exec_prompt_module="experiments.datasets.SciCode.train.template.op_prompt",
        data_file_pattern="data/scicode_{split}.jsonl",
        operator_registry="experiments.datasets.SciCode.train.template.operator_registry",
        default_architecture=[["Testing", "ReAct"]],
        semaphore_divisor=2,
    ),
}


def get_spec(dataset: str) -> DatasetSpec:
    """Return the DatasetSpec for *dataset*, or raise ValueError."""
    try:
        return REGISTRY[dataset]
    except KeyError:
        raise ValueError(f"Unknown dataset: {dataset!r}. Available: {', '.join(sorted(REGISTRY))}") from None


def import_benchmark_class(dataset: str) -> type:
    """Dynamically import and return the benchmark class for *dataset*."""
    spec = get_spec(dataset)
    module = importlib.import_module(spec.benchmark_module)
    return getattr(module, spec.benchmark_class)


def import_workflow(dataset: str, split: str) -> type:
    """Import and return the Workflow class for *dataset* and *split*.

    *split* should be ``"train"`` or ``"test"``.
    """
    spec = get_spec(dataset)
    module_path = spec.workflow_pattern.format(split=split)
    module = importlib.import_module(module_path)
    return module.Workflow


def import_post_exec_prompt(dataset: str) -> str | None:
    """Import and return SPECIALIST_POST_EXEC_PROMPT for *dataset*.

    Returns ``None`` if the module or attribute does not exist.
    """
    spec = get_spec(dataset)
    try:
        module = importlib.import_module(spec.post_exec_prompt_module)
        return getattr(module, "SPECIALIST_POST_EXEC_PROMPT", None)
    except (ImportError, ModuleNotFoundError):
        return None
