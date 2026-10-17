"""Detection helpers for release-ready LLMPrint verification."""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import torch


DEFAULT_Z_SCORE = 1.64
DEFAULT_GRAYBOX_PROB_THRESHOLD = 1e-3

DEFAULT_VALIDATION_NEGATIVE_MODEL_IDS = [
    "bigscience/bloom-560m",
    "distilbert/distilgpt2",
    "facebook/opt-1.3b",
    "facebook/opt-350m",
    "google/gemma-2b",
    "google/gemma-3-1b-it",
    "microsoft/phi-2",
    "microsoft/Phi-3-mini-128k-instruct",
    "openai-community/gpt2",
    "Qwen/Qwen2-7B",
    "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "tiiuae/Falcon3-7B-Base",
]

DEFAULT_VALIDATION_NEGATIVES_PATH = (
    Path(__file__).resolve().parent / "model_lists" / "validation_negatives.pt"
)


def sequence_to_bits(sequence: Sequence[Sequence[float]]) -> List[int]:
    """Convert a probability/frequency sequence into a bit string."""
    bits: List[int] = []
    for score_pos, score_neg in sequence:
        bits.append(1 if score_pos >= score_neg else 0)
    return bits


def compute_bitwise_accuracy(
    base_sequence: Sequence[Sequence[float]],
    compare_sequence: Sequence[Sequence[float]],
) -> float:
    """Compute plain bitwise accuracy between two sequences."""
    if len(base_sequence) != len(compare_sequence):
        raise ValueError("Base and compare sequences must have the same length.")
    if not base_sequence:
        return 0.0

    base_bits = sequence_to_bits(base_sequence)
    compare_bits = sequence_to_bits(compare_sequence)
    matches = sum(base_bit == compare_bit for base_bit, compare_bit in zip(base_bits, compare_bits))
    return matches / len(base_bits)


def get_graybox_filtered_bits(
    base_sequence: Sequence[Sequence[float]],
    compare_sequence: Sequence[Sequence[float]],
    threshold: float = DEFAULT_GRAYBOX_PROB_THRESHOLD,
) -> Tuple[List[int], List[int]]:
    """Return filtered gray-box bits."""
    if len(base_sequence) != len(compare_sequence):
        raise ValueError("Base and compare sequences must have the same length.")

    filtered_base: List[int] = []
    filtered_compare: List[int] = []
    for (base_pos, base_neg), (cmp_pos, cmp_neg) in zip(base_sequence, compare_sequence):
        if min(base_pos, base_neg) > threshold and min(cmp_pos, cmp_neg) > threshold:
            filtered_base.append(1 if base_pos > base_neg else 0)
            filtered_compare.append(1 if cmp_pos > cmp_neg else 0)
    return filtered_base, filtered_compare


def compute_valid_n(
    base_sequence: Sequence[Sequence[float]],
    compare_sequence: Sequence[Sequence[float]],
    threshold: float = DEFAULT_GRAYBOX_PROB_THRESHOLD,
) -> int:
    """Count valid gray-box positions after threshold filtering."""
    filtered_base, _ = get_graybox_filtered_bits(
        base_sequence,
        compare_sequence,
        threshold=threshold,
    )
    return len(filtered_base)


def sanitize_model_id(model_id: str) -> str:
    return model_id.replace("/", "_").replace(":", "_").replace(".__snapshots_", "")


def split_model_ref_for_filename(model_ref: str) -> Tuple[str, str]:
    model_path = Path(model_ref)
    if model_path.exists():
        return "local", model_path.name
    if "/" in model_ref and not model_ref.startswith("/"):
        return model_ref.split("/", 1)
    return "unknown", model_ref


def model_ref_to_result_filename(model_ref: str) -> str:
    author, model = split_model_ref_for_filename(model_ref)
    return f"prob_sequence_{sanitize_model_id(author)}_{sanitize_model_id(model)}.pt"


def binomial_pvalue_greater(successes: int, trials: int, p: float = 0.5) -> float:
    """Return the one-sided exact binomial p-value P[X >= successes]."""
    if trials <= 0:
        return 1.0
    if successes <= 0:
        return 1.0
    if successes > trials:
        return 0.0

    return float(
        sum(
            math.comb(trials, outcome) * (p ** outcome) * ((1.0 - p) ** (trials - outcome))
            for outcome in range(successes, trials + 1)
        )
    )


def estimate_threshold_from_irrelevant(
    irrel_pairs: Iterable[Tuple[Sequence[Sequence[float]], Sequence[Sequence[float]]]],
    z_score: float = DEFAULT_Z_SCORE,
) -> float:
    """Estimate the paper's Gaussian detection threshold tau = mu + z * sigma."""
    accuracies = np.array(
        [compute_bitwise_accuracy(base_seq, compare_seq) for base_seq, compare_seq in irrel_pairs],
        dtype=np.float64,
    )
    if accuracies.size == 0:
        raise ValueError("No validation-negative pairs available for threshold calibration.")

    mean = float(np.mean(accuracies))
    std = float(np.std(accuracies, ddof=1)) if accuracies.size > 1 else 0.0
    threshold = mean + z_score * std
    return float(min(1.0, threshold))


def estimate_min_n_from_irrelevant(
    irrel_pairs: Iterable[Tuple[Sequence[Sequence[float]], Sequence[Sequence[float]]]],
    threshold: float = DEFAULT_GRAYBOX_PROB_THRESHOLD,
) -> int:
    """Estimate the gray-box minimum valid-bit count from validation negatives."""
    valid_counts = []
    for base_sequence, compare_sequence in irrel_pairs:
        valid_n = compute_valid_n(base_sequence, compare_sequence, threshold=threshold)
        if valid_n > 0:
            valid_counts.append(valid_n)

    if len(valid_counts) < 3:
        print("Warning: not enough valid validation-negative pairs for gray-box min_n.")
        return 0

    # Use the strictest observed valid-bit count so gray-box evaluation
    # never accepts fewer positions than were available during calibration.
    return max(valid_counts)


def load_validation_negative_model_ids(
    path: Path = DEFAULT_VALIDATION_NEGATIVES_PATH,
) -> List[str]:
    if path.exists():
        obj = torch.load(path, map_location="cpu")
        if isinstance(obj, list):
            return [str(item) for item in obj]
    return list(DEFAULT_VALIDATION_NEGATIVE_MODEL_IDS)


def resolve_validation_negative_filenames(
    validation_items: Iterable[str] | None = None,
) -> List[str]:
    items = list(validation_items) if validation_items is not None else load_validation_negative_model_ids()
    filenames = []
    for item in items:
        if item.endswith(".pt") and item.startswith("prob_sequence_"):
            filenames.append(item)
        else:
            filenames.append(model_ref_to_result_filename(item))
    return filenames


def _select_validation_files(
    compare_folder: str,
    validation_files: Iterable[str] | None = None,
) -> List[str]:
    candidate_files = sorted(
        file_name
        for file_name in os.listdir(compare_folder)
        if file_name.endswith(".pt")
    )
    allowed = set(resolve_validation_negative_filenames(validation_files))
    selected = [file_name for file_name in candidate_files if file_name in allowed]
    missing = sorted(allowed - set(selected))
    if missing:
        print(
            f"[warn] Missing {len(missing)} validation-negative files in {compare_folder}: "
            f"{', '.join(missing[:3])}"
            + (" ..." if len(missing) > 3 else "")
        )
    return selected


def get_validation_negative_pairs(
    compare_folder: str,
    base_sequence: Sequence[Sequence[float]],
    validation_files: Iterable[str] | None = None,
) -> List[Tuple[Sequence[Sequence[float]], Sequence[Sequence[float]]]]:
    """Load calibration pairs from the validation-negative model set."""
    selected_files = _select_validation_files(compare_folder, validation_files=validation_files)
    pairs: List[Tuple[Sequence[Sequence[float]], Sequence[Sequence[float]]]] = []
    for file_name in selected_files:
        file_path = os.path.join(compare_folder, file_name)
        compare_sequence = torch.load(file_path).tolist()
        if len(base_sequence) != len(compare_sequence):
            continue
        pairs.append((base_sequence, compare_sequence))
    return pairs
