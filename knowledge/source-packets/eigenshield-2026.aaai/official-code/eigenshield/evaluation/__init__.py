"""Evaluation utilities for EigenShield."""

from .metrics import (
    PerspectiveAPIScorer,
    HarmClassifier,
    AttackSuccessEvaluator,
    compute_asr,
    compute_toxicity_metrics,
)

from .datasets import (
    RealToxicityPromptsDataset,
    HarmBenchDataset,
    JailbreakDataset,
)

from .evaluator import (
    EigenShieldEvaluator,
    EvaluationConfig,
    EvaluationResults,
    run_llm_evaluation,
    run_vlm_evaluation,
)

__all__ = [
    # Metrics
    "PerspectiveAPIScorer",
    "HarmClassifier", 
    "AttackSuccessEvaluator",
    "compute_asr",
    "compute_toxicity_metrics",
    # Datasets
    "RealToxicityPromptsDataset",
    "HarmBenchDataset",
    "JailbreakDataset",
    # Evaluator
    "EigenShieldEvaluator",
    "EvaluationConfig",
    "EvaluationResults",
    "run_llm_evaluation",
    "run_vlm_evaluation",
]
