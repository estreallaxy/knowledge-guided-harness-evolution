#!/usr/bin/env python3
"""
calculate_memory.py – Add memory calculation columns to a results CSV.

Now supports:
- Eviction methods ("eviction" column):
  * rkv_<BUDGET>              → effective tokens = min(BUDGET, avg_tokens)
  * streamingllm_<A>_<W>      → effective tokens = min(A+W, avg_tokens)
    (A is (budget - window_size), W is window_size)
  * anything else / missing   → effective tokens = avg_tokens

- HQQ KV cache quantization (via "kv_precision" like: hqq_8, hqq_4, ...):
  * Ignores residuals (treat as fully quantized)
  * Assumes q_group_size=64 and scales dtype = bf16 (2 bytes)
  * Computes bytes/token from the fp16 baseline kv_kb_per_token in config:
        Let W = kv_width * n_layers (unknown individually, but:
            fp16_total_bytes_per_token = 4 * W  ⇒  W = (kv_kb_per_token * 1024) / 4 = kv_kb_per_token * 256)
        Then HQQ bytes/token = W*(nbits/4) + (W/64)*4   (K+V included, scales per group per tensor)

- FP8 rule unchanged: if 'fp8' in kv_precision, halve the baseline kv_kb_per_token.

All other cases use the baseline fp16/bf16 kv_kb_per_token from the config.
"""

import os
import json
import time
import shutil
import argparse
import tempfile
from pathlib import Path
import pandas as pd
import re
from typing import Optional


_RKV_RE = re.compile(r"^\s*rkv[ _\-]?(\d+)\s*$", re.IGNORECASE)
_STM_RE = re.compile(r"^\s*streamingllm[ _\-]?(\d+)[ _\-]+(\d+)\s*$", re.IGNORECASE)

def _get_model_weight_size_gb(model_name: str,
                              weight_precision: str,
                              weight_quant: Optional[str],
                              model_sizes: dict,
                              model_sizes_scheme: Optional[dict] = None) -> Optional[float]:
    """
    Resolve model weight size (GB) with optional quant scheme overrides.
    Precedence:
      1) model_size_gb_scheme[model][f\"{quant}_{prec}\"] (e.g., 'awq_4', 'gptq_4', 'fp8_8')
      2) model_size_gb[model][f\"{prec}_{quant}\"] (e.g., '4_awq', '4_gptq', '8_fp8')
      3) model_size_gb[model][prec] (fallback) — only allowed for GPTQ or when quantization is unspecified
         (treat '', 'nan', 'none', 'null' as unspecified).
         For non-GPTQ quant methods (e.g., 'awq', 'fp8'), a missing method-specific entry raises an error.
    """
    model_key = str(model_name)
    prec_key = str(weight_precision)
    quant_key = (weight_quant or "").lower().strip()
    # Normalize unspecified quant values coming from CSV/NaN
    if quant_key in {"", "nan", "none", "null"}:
        quant_key = ""
    # 1) Scheme block
    if model_sizes_scheme and model_key in model_sizes_scheme and quant_key:
        scheme_map = model_sizes_scheme.get(model_key) or {}
        direct_key = f"{quant_key}_{prec_key}"
        if direct_key in scheme_map:
            return scheme_map[direct_key]
    # 2) Suffix inside primary block
    base_map = (model_sizes.get(model_key) or {}) if isinstance(model_sizes, dict) else {}
    if quant_key:
        alt1 = f"{prec_key}_{quant_key}"
        alt2 = f"{quant_key}_{prec_key}"
        if alt1 in base_map:
            return base_map[alt1]
        if alt2 in base_map:
            return base_map[alt2]
    # 3) Fallback to plain precision — allowed only when:
    #    - quantization method is unspecified, or
    #    - quantization method is GPTQ (incl. variants containing 'gptq').
    allow_plain_fallback = (not quant_key) or ("gptq" in quant_key)
    if allow_plain_fallback and prec_key in base_map:
        return base_map[prec_key]
    # If a non-GPTQ quant method was requested but no explicit mapping exists, raise an error.
    if quant_key and ("gptq" not in quant_key):
        raise KeyError(
            f"Missing model_size_gb for model='{model_key}' with quant='{quant_key}' and precision='{prec_key}'. "
            f"Add an entry to 'model_size_gb_scheme[{model_key!s}]' as '{quant_key}_{prec_key}', or to "
            f"'model_size_gb[{model_key!s}]' as '{prec_key}_{quant_key}' or '{quant_key}_{prec_key}'."
        )
    return None

def _parse_eviction_label(eviction: str, avg_tokens: float) -> float:
    """Return effective token count used to size KV cache."""
    if eviction is None:
        return float(avg_tokens)
    ev = str(eviction).strip()
    if not ev or ev.lower() == "nan":
        return float(avg_tokens)

    m = _RKV_RE.match(ev)
    if m:
        budget = int(m.group(1))
        return float(min(budget, avg_tokens))

    m = _STM_RE.match(ev)
    if m:
        a = int(m.group(1))
        w = int(m.group(2))
        budget = a + w
        return float(min(budget, avg_tokens))

    # Unknown label → fall back to avg_tokens
    return float(avg_tokens)


def _kv_bytes_per_token_from_row(row: pd.Series, kv_lookups: dict) -> float:
    """
    Compute KV BYTES per token for this row, using:
    - HQQ formula if kv_precision like 'hqq_8' / 'hqq_4' etc. (ignores residual).
    - FP8 → halve baseline.
    - Otherwise use baseline kv_kb_per_token from config.

    Returns:
        bytes per token (float).
    """
    model_name = row.get("model")
    kv_precision = str(row.get("kv_precision", "")).lower()

    # Baseline KB/token from config (fp16/bf16 baseline, K+V across all layers)
    kv_kb_per_token = kv_lookups.get(model_name)
    if kv_kb_per_token is None:
        raise KeyError(f"No kv_kb_per_token baseline in config for model='{model_name}'")

    # HQQ path: kv_precision like 'hqq_8'
    # Assumptions: group_size=64, bf16 scales (2 bytes), ignore residual window.
    if kv_precision.startswith("hqq_"):
        # Extract nbits (default to 8 if parse fails)
        try:
            nbits = int(kv_precision.split("_", 1)[1])
        except Exception:
            nbits = 8

        group_size = 64  # fixed per requirement

        # Let W = kv_width * n_layers. From fp16 baseline:
        # fp16_total_bytes_per_token = 4 * W  (2 bytes/elem * 2 tensors K/V)
        # kv_kb_per_token is KB/token → bytes/token = kv_kb_per_token * 1024
        # ⇒ W = (kv_kb_per_token * 1024) / 4 = kv_kb_per_token * 256
        W = float(kv_kb_per_token) * 256.0

        # HQQ total bytes/token (K+V):
        #   data  : 2 * kv_width * (nbits/8)  →  (nbits/4) * kv_width
        #   scales: 2 * (kv_width/group_size) * 2 bytes(bf16)  →  (kv_width/group_size) * 4
        # Across all layers: replace kv_width by W (kv_width * n_layers).
        # ⇒ bytes/token = W*(nbits/4) + (W/group_size)*4
        bytes_per_token = W * (nbits / 4.0) + (W / float(group_size)) * 4.0
        return float(bytes_per_token)

    # FP8 path: halve baseline KB/token
    if "fp8" in kv_precision:
        return float(kv_kb_per_token) * 1024.0 / 2.0

    # Default: use baseline KB/token
    return float(kv_kb_per_token) * 1024.0


def calculate_memory_usage(row: pd.Series, model_sizes: dict, kv_lookups: dict, model_sizes_scheme: Optional[dict] = None) -> tuple:
    """
    Calculates model size, KV cache size, and total memory for a single row.

    Args:
        row: A pandas Series representing one row of the results DataFrame.
        model_sizes: A dictionary mapping model -> precision -> size_in_GB.
        kv_lookups: A dictionary mapping model -> kv_kb_per_token (fp16 baseline).

    Returns:
        A tuple (model_size_gb, kv_size_gb, total_memory_gb), each rounded.
        Returns (None, None, None) if required data is missing.
    """
    model_name = row.get("model")
    weight_precision = str(row.get("weight_precision"))
    weight_quant = str(row.get("weight_quant", "") or "")
    avg_tokens = float(row.get("avg_tokens"))
    # Parse group_size; allow forms like "prm_4"
    raw_gs = row.get("group_size")
    is_prm = False
    try:
        group_size = float(raw_gs)
    except Exception:
        s = str(raw_gs or "").strip().lower()
        if s.startswith("prm"):
            is_prm = True
            m = re.search(r"(\d+)", s)
            group_size = float(m.group(1)) if m else 1.0
        else:
            m = re.search(r"(\d+)", s)
            group_size = float(m.group(1)) if m else 1.0
    kv_precision = str(row.get("kv_precision", "")).lower()
    eviction = row.get("kv_eviction", "")

    # 1) Model size (GB) with quant scheme overrides
    model_size_gb = _get_model_weight_size_gb(model_name, weight_precision, weight_quant, model_sizes, model_sizes_scheme)

    # 2) KV bytes/token (from baseline or HQQ/FP8 logic)
    try:
        kv_bytes_per_token = _kv_bytes_per_token_from_row(row, kv_lookups)
    except KeyError as e:
        print(f"⚠️ Warning: {e}. Skipping row.")
        return None, None, None

    if model_size_gb is None:
        extra = f", quant='{weight_quant}'" if weight_quant else ""
        print(f"⚠️ Warning: No model_size_gb for model='{model_name}' with precision='{weight_precision}'{extra}. Skipping row.")
        return None, None, None

    # 3) Apply eviction cap: effective tokens for sizing KV
    effective_tokens = _parse_eviction_label(eviction, avg_tokens)

    # 4) KV total size (GB)
    # bytes/token * tokens * parallel sequences
    kv_total_bytes = kv_bytes_per_token * effective_tokens * group_size
    kv_size_gb = kv_total_bytes / (1024.0 ** 3)

    total_memory_gb = float(model_size_gb) + float(kv_size_gb)

    # PRM constant memory (not multiplied by group size), taken from config under key "prm"
    prm_const_gb = row.get("_prm_constant_gb", None)
    if is_prm and prm_const_gb is not None:
        try:
            total_memory_gb += float(prm_const_gb)
        except Exception:
            pass

    return round(float(model_size_gb), 3), round(float(kv_size_gb), 3), round(float(total_memory_gb), 3)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append memory calculation columns (model_size_gb, kv_size_gb, total_memory_gb) to a CSV file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--input-csv",
        required=True,
        help="Input CSV file (will be modified in-place)."
    )
    parser.add_argument(
        "--config-json",
        required=True,
        help="JSON file containing memory lookup tables for models."
    )
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    config_path = Path(args.config_json)

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV file not found at: {input_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"Config JSON file not found at: {config_path}")

    try:
        df = pd.read_csv(input_path)
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        model_sizes = config.get("model_size_gb", {})
        kv_lookups = config.get("kv_kb_per_token", {})
        model_sizes_scheme = config.get("model_size_gb_scheme", {})
        prm_constant_gb = float(config.get("prm", 0.0))
    except Exception as e:
        print(f"❌ Error loading data or config file: {e}")
        return

    # Warn if PRM rows exist but config has no 'prm' key
    try:
        has_prm_rows = df.get("group_size") is not None and df["group_size"].astype(str).str.lower().str.contains("prm").any()
    except Exception:
        has_prm_rows = False
    if has_prm_rows and ("prm" not in config):
        print("⚠️ Warning: Config JSON has no 'prm' key, but PRM rows are present. "
              "Proceeding with prm=0.0 GB (no additional constant memory).")

    # Required columns (eviction is optional; we fall back to avg_tokens if missing)
    required_cols = {"model", "weight_precision", "avg_tokens", "group_size", "kv_precision"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Input CSV is missing required column(s): {missing}")

    print("⚙️ Calculating memory usage for each row...")
    # Inject PRM constant as a temporary column for per-row access
    df["_prm_constant_gb"] = prm_constant_gb
    results = df.apply(lambda row: calculate_memory_usage(row, model_sizes, kv_lookups, model_sizes_scheme),
                       axis=1, result_type='expand')

    df["model_size_gb"] = results[0]
    df["kv_size_gb"] = results[1]
    df["total_memory_gb"] = results[2]
    # Cleanup temp column
    if "_prm_constant_gb" in df.columns:
        df.drop(columns=["_prm_constant_gb"], inplace=True)

    try:
        backup_path = input_path.with_suffix(f".{time.strftime('%Y%m%d_%H%M%S')}.bak")
        shutil.copy2(input_path, backup_path)

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".csv", dir=input_path.parent) as tmp:
            temp_path = Path(tmp.name)

        df.to_csv(temp_path, index=False)
        os.replace(temp_path, input_path)

        print(f"\n✅ Successfully added memory columns to '{input_path}'.")
        print(f"📄 A backup of the original file has been saved to '{backup_path.name}'.")
    except Exception as e:
        print(f"\n❌ An error occurred while writing the output file: {e}")


if __name__ == "__main__":
    main()
