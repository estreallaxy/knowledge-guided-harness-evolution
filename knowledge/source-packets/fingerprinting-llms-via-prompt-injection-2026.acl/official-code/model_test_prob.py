"""Evaluate detection rates from saved probability sequences."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import torch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from detect_func import (
    DEFAULT_GRAYBOX_PROB_THRESHOLD,
    DEFAULT_Z_SCORE,
    binomial_pvalue_greater,
    compute_bitwise_accuracy,
    estimate_min_n_from_irrelevant,
    estimate_threshold_from_irrelevant,
    get_graybox_filtered_bits,
    get_validation_negative_pairs,
    model_ref_to_result_filename,
)


RESULT_METADATA_FILENAME = "result_metadata.json"
PAIR_MANIFEST_FILENAME = "pair_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute detection rates from saved probability sequences.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default="meta-llama/Meta-Llama-3-8B",
        help="Base model identifier used to locate the reference sequence.",
    )
    parser.add_argument(
        "--detect-type",
        choices=["graybox", "blackbox"],
        default="graybox",
        help="Detection mode to evaluate.",
    )
    parser.add_argument(
        "--result-root",
        type=str,
        default="./results",
        help="Root directory containing probability-sequence folders produced by produce_prob_finetune_batch.py.",
    )
    parser.add_argument(
        "--adv-dir",
        type=str,
        default=None,
        help="Adversarial suffix directory used to infer default result folders. When omitted, the script falls back to the legacy folder names.",
    )
    parser.add_argument(
        "--pair-count",
        type=int,
        default=300,
        help="Number of prompt pairs encoded in the result-folder name.",
    )
    parser.add_argument(
        "--base-sequence-path",
        type=str,
        default=None,
        help="Optional explicit path to the base model probability sequence. Overrides the inferred default.",
    )
    parser.add_argument(
        "--irrelevant-folder",
        type=str,
        default=None,
        help="Optional explicit path to the validation-negative result folder. Overrides the inferred default.",
    )
    parser.add_argument(
        "--compare-folder",
        action="append",
        default=[],
        help="Repeatable mapping of the form <label>=<path>. Overrides the inferred default comparison folders.",
    )
    parser.add_argument(
        "--base-split-label",
        type=str,
        default="relevant",
        help="Split label used to locate the base-model sequence when --adv-dir is provided.",
    )
    parser.add_argument(
        "--calibration-split-label",
        type=str,
        default="holdout",
        help="Split label used to locate the validation-negative folder when --adv-dir is provided.",
    )
    parser.add_argument(
        "--compare-split",
        action="append",
        default=[],
        help="Repeatable mapping of the form <label>=<split_label>. Defaults to finetune=relevant and irrelevant=irrelevant when --adv-dir is provided.",
    )
    parser.add_argument(
        "--validation-negatives-path",
        type=str,
        default=None,
        help="Optional .pt path containing a List[str] of validation-negative model ids.",
    )
    parser.add_argument(
        "--include-base-model-in-rate",
        action="store_true",
        help="Include the base model file itself when reporting detection rates for comparison folders.",
    )
    parser.add_argument(
        "--graybox-prob-threshold",
        type=float,
        default=DEFAULT_GRAYBOX_PROB_THRESHOLD,
        help="Probability threshold used to keep gray-box bits.",
    )
    parser.add_argument(
        "--z-score",
        type=float,
        default=DEFAULT_Z_SCORE,
        help="Z-score used for black-box threshold calibration.",
    )
    return parser.parse_args()


def infer_model_tag(model_ref: str) -> str:
    model_path = Path(model_ref)
    if model_path.exists():
        return model_path.name
    return model_ref.rsplit("/", 1)[-1]


def normalize_path_string(path_str: str | None) -> str | None:
    if path_str is None:
        return None
    try:
        return str(Path(path_str).resolve())
    except OSError:
        return str(Path(path_str))


def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Unsupported JSON structure in {path}: {type(data)}")
    return data


def load_result_metadata(result_dir: Path) -> Optional[Dict[str, Any]]:
    return load_json_file(result_dir / RESULT_METADATA_FILENAME)


def load_pair_manifest_pairs(result_dir: Path) -> Optional[List[Tuple[str, str]]]:
    payload = load_json_file(result_dir / PAIR_MANIFEST_FILENAME)
    if payload is None:
        return None

    raw_pairs = payload.get("pairs")
    if not isinstance(raw_pairs, list):
        raise ValueError(f"Invalid pair manifest in {result_dir / PAIR_MANIFEST_FILENAME}")

    pairs: List[Tuple[str, str]] = []
    for item in raw_pairs:
        if not isinstance(item, list) or len(item) < 2:
            raise ValueError(f"Invalid pair entry in {result_dir / PAIR_MANIFEST_FILENAME}: {item!r}")
        pairs.append((str(item[0]), str(item[1])))
    return pairs


def validate_manifest_length(result_dir: Path, sequence_length: int) -> None:
    manifest_pairs = load_pair_manifest_pairs(result_dir)
    if manifest_pairs is None:
        return
    if len(manifest_pairs) != sequence_length:
        raise ValueError(
            f"Pair manifest length mismatch in {result_dir}: "
            f"manifest has {len(manifest_pairs)} pairs but sequence has {sequence_length} rows."
        )


def ensure_matching_pair_manifests(
    reference_dir: Path,
    compare_dir: Path,
    label: str,
) -> None:
    reference_pairs = load_pair_manifest_pairs(reference_dir)
    compare_pairs = load_pair_manifest_pairs(compare_dir)

    if reference_pairs is None or compare_pairs is None:
        if reference_pairs is None and compare_pairs is None:
            return
        print(
            f"[warn] Pair manifest missing for {label}; cannot verify pair order between "
            f"{reference_dir} and {compare_dir}."
        )
        return

    if reference_pairs != compare_pairs:
        raise ValueError(
            f"Pair manifest mismatch for {label}: {reference_dir} and {compare_dir} "
            "were not generated from the same ordered pair list."
        )


def metadata_matches(
    result_dir: Path,
    *,
    base_model: str,
    detect_type: str,
    split_label: str,
    pair_count: int,
    adv_dir: str | None,
) -> bool:
    metadata = load_result_metadata(result_dir)
    if metadata is None:
        return False

    if metadata.get("detect_type") != detect_type:
        return False
    if metadata.get("split_label") != split_label:
        return False
    if metadata.get("requested_pair_count") != pair_count:
        return False

    base_model_tag = infer_model_tag(base_model)
    metadata_base_model = metadata.get("base_model")
    metadata_base_model_tag = metadata.get("base_model_tag")
    if metadata_base_model != base_model and metadata_base_model_tag != base_model_tag:
        return False

    if adv_dir is None:
        return True

    adv_path = Path(adv_dir)
    candidates = {str(adv_path), adv_path.name}
    normalized_adv_path = normalize_path_string(adv_dir)
    if normalized_adv_path is not None:
        candidates.add(normalized_adv_path)

    for key in ("adv_dir", "adv_dir_name", "adv_dir_resolved"):
        value = metadata.get(key)
        if isinstance(value, str) and value in candidates:
            return True
    return False


def find_result_dir_by_metadata(
    base_model: str,
    detect_type: str,
    result_root: str,
    adv_dir: str | None,
    pair_count: int,
    split_label: str,
) -> Optional[str]:
    if adv_dir is None:
        return None

    result_root_path = Path(result_root)
    if not result_root_path.is_dir():
        return None

    matches = []
    for child in sorted(result_root_path.iterdir()):
        if not child.is_dir():
            continue
        if metadata_matches(
            child,
            base_model=base_model,
            detect_type=detect_type,
            split_label=split_label,
            pair_count=pair_count,
            adv_dir=adv_dir,
        ):
            matches.append(child)

    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(
            f"Multiple result folders matched metadata for split={split_label}: "
            + ", ".join(str(path) for path in matches)
        )
    return str(matches[0])


def build_result_dir(
    base_model: str,
    adv_dir: str,
    detect_type: str,
    result_root: str,
    pair_count: int,
    loss_type: str = "target",
    split_label: str = "relevant",
) -> str:
    base = infer_model_tag(base_model)
    adv_name = Path(adv_dir).name
    parts = adv_name.split("_")

    try:
        adv_type = parts[parts.index("adv") + 1]
    except Exception:
        adv_type = "unknown"

    variant = ""
    try:
        idx_ids = parts.index("ids")
        loss_type = parts[idx_ids + 1] if idx_ids + 1 < len(parts) else loss_type
        extra = parts[idx_ids + 2 :] if idx_ids + 2 < len(parts) else []
        if extra:
            variant = "_".join(extra)
    except Exception:
        pass

    subdir = f"prob_{adv_type}_{pair_count}_{base}_{detect_type}_{loss_type}"
    if variant:
        subdir += f"_{variant}"
    subdir += f"_{split_label}"
    return str(Path(result_root) / subdir)


def build_legacy_default_compare_folders(base_model: str, detect_type: str) -> Dict[str, str]:
    model_tag = infer_model_tag(base_model)
    return {
        f"finetune_{detect_type}": f"./prob_suffix_300_{model_tag}_{detect_type}_target_relevant",
        f"irrelevant_{detect_type}": f"./prob_suffix_300_{model_tag}_{detect_type}_target_irrelevant",
    }


def build_legacy_default_irrelevant_folder(base_model: str, detect_type: str) -> str:
    model_tag = infer_model_tag(base_model)
    return f"./prob_suffix_300_{model_tag}_{detect_type}_target_holdout"


def build_legacy_default_base_sequence_path(base_model: str, detect_type: str) -> str:
    model_tag = infer_model_tag(base_model)
    relevant_folder = Path(f"./prob_suffix_300_{model_tag}_{detect_type}_target_relevant")
    return str(relevant_folder / model_ref_to_result_filename(base_model))


def parse_named_mapping(
    raw_items: Iterable[str],
    *,
    default_mapping: Dict[str, str],
    arg_name: str,
) -> Dict[str, str]:
    if not raw_items:
        return dict(default_mapping)

    parsed: Dict[str, str] = {}
    for raw in raw_items:
        if "=" not in raw:
            raise ValueError(f"Invalid {arg_name} value: {raw}. Expected format <label>=<value>.")
        label, value = raw.split("=", 1)
        label = label.strip()
        value = value.strip()
        if not label or not value:
            raise ValueError(f"Invalid {arg_name} value: {raw}. Expected non-empty <label>=<value>.")
        parsed[label] = value
    return parsed


def resolve_result_dir(
    base_model: str,
    detect_type: str,
    result_root: str,
    adv_dir: str | None,
    pair_count: int,
    split_label: str,
) -> str:
    metadata_match = find_result_dir_by_metadata(
        base_model=base_model,
        detect_type=detect_type,
        result_root=result_root,
        adv_dir=adv_dir,
        pair_count=pair_count,
        split_label=split_label,
    )
    if metadata_match is not None:
        return metadata_match

    if adv_dir is None:
        raise ValueError("resolve_result_dir requires adv_dir when metadata lookup is unavailable.")

    return build_result_dir(
        base_model,
        adv_dir,
        detect_type,
        result_root,
        pair_count,
        split_label=split_label,
    )


def build_default_compare_folders(
    base_model: str,
    detect_type: str,
    result_root: str,
    adv_dir: str | None,
    pair_count: int,
    compare_splits: Iterable[str],
) -> Dict[str, str]:
    if adv_dir is None:
        return build_legacy_default_compare_folders(base_model, detect_type)

    split_mapping = parse_named_mapping(
        compare_splits,
        default_mapping={"finetune": "relevant", "irrelevant": "irrelevant"},
        arg_name="--compare-split",
    )
    return {
        label: resolve_result_dir(
            base_model=base_model,
            detect_type=detect_type,
            result_root=result_root,
            adv_dir=adv_dir,
            pair_count=pair_count,
            split_label=split_label,
        )
        for label, split_label in split_mapping.items()
    }


def build_default_irrelevant_folder(
    base_model: str,
    detect_type: str,
    result_root: str,
    adv_dir: str | None,
    pair_count: int,
    split_label: str,
) -> str:
    if adv_dir is None:
        return build_legacy_default_irrelevant_folder(base_model, detect_type)
    return resolve_result_dir(
        base_model=base_model,
        detect_type=detect_type,
        result_root=result_root,
        adv_dir=adv_dir,
        pair_count=pair_count,
        split_label=split_label,
    )


def build_default_base_sequence_path(
    base_model: str,
    detect_type: str,
    result_root: str,
    adv_dir: str | None,
    pair_count: int,
    split_label: str,
) -> str:
    if adv_dir is None:
        return build_legacy_default_base_sequence_path(base_model, detect_type)

    result_dir = resolve_result_dir(
        base_model=base_model,
        detect_type=detect_type,
        result_root=result_root,
        adv_dir=adv_dir,
        pair_count=pair_count,
        split_label=split_label,
    )
    return str(Path(result_dir) / model_ref_to_result_filename(base_model))


def parse_compare_folders(
    compare_folders: Iterable[str],
    compare_splits: Iterable[str],
    base_model: str,
    detect_type: str,
    result_root: str,
    adv_dir: str | None,
    pair_count: int,
) -> Dict[str, str]:
    if not compare_folders:
        return build_default_compare_folders(
            base_model,
            detect_type,
            result_root,
            adv_dir,
            pair_count,
            compare_splits,
        )

    parsed: Dict[str, str] = {}
    for raw in compare_folders:
        if "=" not in raw:
            raise ValueError(
                f"Invalid --compare-folder value: {raw}. Expected format <label>=<path>."
            )
        label, folder = raw.split("=", 1)
        parsed[label] = folder
    return parsed


def load_validation_negative_items(path: str | None) -> List[str] | None:
    if path is None:
        return None

    obj = torch.load(path, map_location="cpu")
    if not isinstance(obj, list):
        raise ValueError(f"Unsupported validation-negative file structure in {path}: {type(obj)}")
    return [str(item) for item in obj]


def evaluate_graybox(
    base_sequence,
    compare_sequence,
    graybox_prob_threshold: float,
    min_n: int,
) -> bool:
    filtered_base, filtered_compare = get_graybox_filtered_bits(
        base_sequence,
        compare_sequence,
        threshold=graybox_prob_threshold,
    )
    correct_bits = sum(
        base_bit == compare_bit for base_bit, compare_bit in zip(filtered_base, filtered_compare)
    )
    total_bits = len(filtered_base)
    pvalue = binomial_pvalue_greater(correct_bits, total_bits, p=0.5)
    return pvalue < 0.05 and total_bits >= min_n


def evaluate_blackbox(base_sequence, compare_sequence, threshold: float) -> bool:
    accuracy = compute_bitwise_accuracy(base_sequence, compare_sequence)
    return accuracy >= threshold


def main() -> None:
    args = parse_args()

    compare_folders = parse_compare_folders(
        args.compare_folder,
        args.compare_split,
        base_model=args.base_model,
        detect_type=args.detect_type,
        result_root=args.result_root,
        adv_dir=args.adv_dir,
        pair_count=args.pair_count,
    )
    irrelevant_folder = args.irrelevant_folder or build_default_irrelevant_folder(
        args.base_model,
        args.detect_type,
        args.result_root,
        args.adv_dir,
        args.pair_count,
        args.calibration_split_label,
    )
    base_sequence_path = args.base_sequence_path or build_default_base_sequence_path(
        args.base_model,
        args.detect_type,
        args.result_root,
        args.adv_dir,
        args.pair_count,
        args.base_split_label,
    )

    if not os.path.exists(base_sequence_path):
        raise FileNotFoundError(f"Cannot find base sequence: {base_sequence_path}")
    if not os.path.isdir(irrelevant_folder):
        raise FileNotFoundError(f"Cannot find validation-negative folder: {irrelevant_folder}")

    base_sequence = torch.load(base_sequence_path, map_location="cpu").tolist()
    base_result_dir = Path(base_sequence_path).parent
    base_sequence_filename = model_ref_to_result_filename(args.base_model)
    validate_manifest_length(base_result_dir, len(base_sequence))
    validate_manifest_length(Path(irrelevant_folder), len(base_sequence))
    ensure_matching_pair_manifests(base_result_dir, Path(irrelevant_folder), "validation negatives")
    validation_negative_items = load_validation_negative_items(args.validation_negatives_path)
    calibration_pairs = get_validation_negative_pairs(
        irrelevant_folder,
        base_sequence,
        validation_files=validation_negative_items,
    )

    if args.detect_type == "graybox":
        min_n = estimate_min_n_from_irrelevant(
            calibration_pairs,
            threshold=args.graybox_prob_threshold,
        )
        print(f"[graybox] estimated min_n: {min_n}")
    else:
        threshold = estimate_threshold_from_irrelevant(
            calibration_pairs,
            z_score=args.z_score,
        )
        print(f"[blackbox] calibrated threshold: {threshold:.6f}")

    for folder_key, compare_folder in compare_folders.items():
        if not os.path.isdir(compare_folder):
            print(f"Directory not found, skip {folder_key}: {compare_folder}")
            continue

        compare_dir = Path(compare_folder)
        validate_manifest_length(compare_dir, len(base_sequence))
        ensure_matching_pair_manifests(base_result_dir, compare_dir, folder_key)

        total_files = 0
        detected = 0
        skipped_base_model = False

        for file_name in sorted(os.listdir(compare_folder)):
            if not file_name.endswith(".pt"):
                continue
            if file_name == base_sequence_filename and not args.include_base_model_in_rate:
                skipped_base_model = True
                continue

            file_path = os.path.join(compare_folder, file_name)
            compare_sequence = torch.load(file_path, map_location="cpu").tolist()

            if len(base_sequence) != len(compare_sequence):
                continue

            if args.detect_type == "graybox":
                is_detected = evaluate_graybox(
                    base_sequence,
                    compare_sequence,
                    graybox_prob_threshold=args.graybox_prob_threshold,
                    min_n=min_n,
                )
            else:
                is_detected = evaluate_blackbox(
                    base_sequence,
                    compare_sequence,
                    threshold=threshold,
                )

            detected += int(is_detected)
            total_files += 1

        if skipped_base_model:
            print(f"[note] skipped base model file in {folder_key}: {base_sequence_filename}")

        if total_files > 0:
            detection_rate = detected / total_files
            print(
                f"Detection Rate for {folder_key} "
                f"({args.detect_type}): {detection_rate:.4f} "
                f"({detected}/{total_files})"
            )
        else:
            print(f"No valid files found for comparison in {folder_key} ({args.detect_type}).")


if __name__ == "__main__":
    main()
