#!/usr/bin/env python3
import os
import json
import csv
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict

# ---------- Model family & quant suffix handling ----------
KNOWLEDGE_VERSION = "2025-11-16"
KNOWN_MODEL_FAMILIES = ['DeepSeek', 'Qwen', 'Llama', 'Mistral', 'Gemma', 'OpenReasoning']

# e.g., -GPTQ-8b, _8bit, -bnb-4b, etc. (trailing)
_QUANT_SUFFIX_RE = re.compile(
    r'(?i)(?:'
    r'(?:[-_](?:gptq|awq|bnb|bitsandbytes|gguf|ggml)[-_]?[a-z0-9]*[-_]?(\d{1,2})b)'
    r'|(?:[-_](\d{1,2})bit)'
    r')$'
)

def extract_model_name(config: Dict[str, Any]) -> str:
    """
    Canonicalize to base family+size (no quant suffix), e.g.:
      - 'Qwen3-32B-GPTQ-8b' -> 'Qwen3-32B'
      - 'skythought_evals_models_Qwen_Qwen3-8B_4bit' -> 'Qwen3-8B'
      - 'deepseek-ai_DeepSeek-R1-Distill-Qwen-14B_4bit' -> 'DeepSeek-R1-Distill-Qwen-14B'
      - 'nvidia_OpenReasoning-Nemotron-1.5B_8bit' -> 'OpenReasoning-Nemotron-1.5B'
    """
    model_cfg = (config.get('model', {}) or {}).get('config', {}) or {}
    s_id = str(model_cfg.get('model_id') or '')
    s_nm = str(model_cfg.get('name') or '')
    hay = f"{s_id} {s_nm}"

    # DeepSeek R1 Distill canonicalization first
    m = re.search(r'deepseek[\W_]*r1[\W_]*distill[\W_]*qwen[\W_-]*([0-9.]+)\s*[bB]', hay, re.IGNORECASE)
    if m:
        return f"DeepSeek-R1-Distill-Qwen-{m.group(1)}B"

    # use last token; strip trailing quant suffix
    last = (s_id.split('/')[-1] if s_id else s_nm) or hay
    last = _QUANT_SUFFIX_RE.sub('', last)

    # Special-case: Qwen3 MoE variants like Qwen3-30B-A3B
    m = re.search(r'(Qwen3-[0-9.]+[Bb]-A3B)', last, flags=re.IGNORECASE) or re.search(r'(Qwen3-[0-9.]+[Bb]-A3B)', hay, flags=re.IGNORECASE)
    if m:
        base = m.group(1)
        base = re.sub(r'[bB]-A3B$', 'B-A3B', base)
        return base.replace('_', '-')

    # Generic: family + size (optionally -A3B)
    pat = r'((?:DeepSeek|Qwen|Llama|Mistral|Gemma|OpenReasoning)[A-Za-z0-9\-]*-[0-9.]+[Bb](?:-A3B)?)'
    m = re.search(pat, last, flags=re.IGNORECASE) or re.search(pat, hay, flags=re.IGNORECASE)
    if m:
        base = m.group(1)
        return re.sub(r'[bB]$', 'B', base).replace('_', '-')

    parts = [p for p in s_id.split('/') if p]
    if parts:
        token = _QUANT_SUFFIX_RE.sub('', parts[-1])
        m = re.search(pat, token, flags=re.IGNORECASE)
        if m:
            return re.sub(r'[bB]$', 'B', m.group(1)).replace('_', '-')

    return model_cfg.get('name', 'unknown_model')

def determine_weight_precision(config: Dict[str, Any]) -> str:
    """
    Determine numeric weight precision '4'/'8'/'16':
      - matches '.../8bit', '_4bit', '-gptq-8b', etc.
      - defaults to '16' if not declared.
    """
    model_cfg = (config.get('model', {}) or {}).get('config', {}) or {}
    candidates = [str(model_cfg.get('name') or ''), str(model_cfg.get('model_id') or '')]

    # explicit ...8bit/4bit/16bit...
    for s in candidates:
        m = re.search(r'(?i)(\d{1,2})\s*bit\b', s)
        if m: return m.group(1)

    # FP8 explicit tags (weights)
    for s in candidates:
        if re.search(r'(?i)\b(fp8|float8|e5m2|e4m3)\b', s):
            return '8'

    # quant suffix like -gptq-8b, -awq-4b
    for s in candidates:
        m = re.search(r'(?i)(?:gptq|awq|bnb|bitsandbytes|gguf|ggml)[-_]?[a-z0-9]*[-_]?(\d{1,2})b\b', s)
        if m: return m.group(1)

    # GPTQ-Int4 pattern (e.g., GPTQ-Int4)
    for s in candidates:
        m = re.search(r'(?i)gptq[^A-Za-z0-9]?[^0-9]*int\s*(\d{1,2})', s)
        if m: return m.group(1)

    # AWQ without explicit bit → assume 4-bit
    for s in candidates:
        if re.search(r'(?i)\bawq\b', s):
            return '4'

    # guarded '/8b' if quant tag elsewhere
    for s in candidates:
        sl = s.lower()
        if re.search(r'(gptq|awq|bnb|bitsandbytes|gguf|ggml)', sl):
            m = re.search(r'[-_/](\d{1,2})b\b', sl)
            if m: return m.group(1)

    return '16'

def determine_weight_quant_scheme(config: Dict[str, Any]) -> str:
    """
    Determine weight quantization scheme, e.g.:
      - 'fp8' if FP8/float8/e5m2/e4m3 present
      - 'awq' if AWQ present (assume 4-bit)
      - 'gptq' if GPTQ present
      - 'bnb'/'bitsandbytes' for bitsandbytes
      - '' if full precision
    """
    model_cfg = (config.get('model', {}) or {}).get('config', {}) or {}
    s_id = str(model_cfg.get('model_id') or '')
    s_nm = str(model_cfg.get('name') or '')
    hay = f"{s_id} {s_nm}".lower()
    if re.search(r'\b(fp8|float8|e5m2|e4m3)\b', hay): return 'fp8'
    if re.search(r'\bawq\b', hay): return 'awq'
    if re.search(r'\bgptq\b', hay): return 'gptq'
    if re.search(r'\b(bitsandbytes|bnb)\b', hay): return 'bnb'
    return ''
# ---------- Family extraction ----------
def _infer_model_family_from_name(model_name: str) -> Optional[str]:
    """
    Given a canonical model name like 'Qwen3-8B' or 'OpenReasoning-Nemotron-7B',
    return the family token (e.g., 'Qwen', 'OpenReasoning', 'DeepSeek', ...).
    """
    s = str(model_name or '')
    first_token = s.split('-', 1)[0]
    for fam in KNOWN_MODEL_FAMILIES:
        if first_token.lower().startswith(fam.lower()):
            return fam
    return None

# ---------- KV precision/eviction ----------
def _first(d: Dict[str, Any], *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default

def _get_cache_impl_and_cfg(cfg: Dict[str, Any]) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    sp = cfg.get('sampling_params', {}) or {}
    model_cfg = (cfg.get('model', {}) or {}).get('config', {}) or {}
    backend = cfg.get('backend', {}) or {}
    be_args = backend.get('backend_args', {}) or {}
    impl = (_first(sp,'cache_implementation') or _first(cfg,'cache_implementation')
            or _first(model_cfg,'cache_implementation') or _first(be_args,'cache_implementation') or '')
    cc = (_first(sp,'cache_config',default={}) or _first(cfg,'cache_config',default={})
          or _first(model_cfg,'cache_config',default={}) or _first(be_args,'cache_config',default={}) or {})
    return str(impl).lower(), dict(cc), dict(be_args)

def _normalize_dtype_tag(val: Any) -> Optional[str]:
    if val is None: return None
    s = str(val).lower()
    if 'bfloat16' in s or s == 'bf16': return 'bf16'
    if 'float16' in s or s == 'fp16' or s == 'half': return 'fp16'
    if 'float32' in s or s == 'fp32' or s == 'full': return 'fp32'
    if 'fp8' in s or 'e5m2' in s or 'e4m3' in s: return 'fp8'
    return None

def compute_kv_precision(cfg: Dict[str, Any]) -> str:
    impl, cc, be_args = _get_cache_impl_and_cfg(cfg)
    if impl == 'quantized' and str(cc.get('backend','')).lower() in ('hqq','quanto'):
        bits = _first(cc,'nbits','bits',default=None)
        if bits is None:
            m = re.search(r'(\d+)', str(cc))
            bits = m.group(1) if m else '8'
        return f"hqq_{int(bits)}"
    dtype = be_args.get('kv_cache_dtype') or cc.get('compute_dtype') or cc.get('dtype')
    tag = _normalize_dtype_tag(dtype)
    if not tag:
        sp = cfg.get('sampling_params', {}) or {}
        tag = _normalize_dtype_tag(sp.get('kv_cache_dtype'))
    return tag or 'fp16'

def compute_kv_eviction(cfg: Dict[str, Any], run_root: str) -> str:
    impl, cc, _ = _get_cache_impl_and_cfg(cfg)
    if impl == 'streamingllm':
        try:
            W = int(cc['window_size']); return f"streamingllm_{W}_{W}"
        except Exception:
            return 'streamingllm'
    if impl == 'rkv':
        b = _first(cc,'budget','max_budget',default=None)
        return f"rkv_{int(b)}" if b is not None else 'rkv'
    return ''

# ---------- Readiness (FAST) ----------
def serial_is_ready_nonzero(summary_data: Dict[str, Any]) -> bool:
    pak = summary_data.get('pass_at_k')
    if isinstance(pak, dict) and pak.get('k=1') is not None:
        return True
    acc = summary_data.get('accuracy', None)
    try:
        return acc is not None and float(acc) > 0.0
    except Exception:
        return False

# ---------- Aggregation ----------
HEADER = ['task','model','weight_precision','weight_quant','kv_precision','kv_eviction',
          'truncated_budget','group_size','num_samples','avg_tokens','accuracy']
KEY_COLS = ['task','model','weight_precision','weight_quant','kv_precision','kv_eviction',
            'truncated_budget','group_size']

def _extract_num_samples(obj: Dict[str, Any], default_if_missing: int = 1, source_hint: str = "") -> int:
    try:
        n = ((obj.get("configuration") or {}).get("sampling_params") or {}).get("n")
        if n is not None:
            v = int(n)
            if v > 0:
                return v
    except Exception:
        pass
    if source_hint:
        print(f"ℹ️  Using default num_samples={default_if_missing} for {source_hint}.")
    return default_if_missing

def _normalize_accuracy_to_pct(val: Optional[float], value_units: str = "auto") -> Optional[float]:
    if val is None: return None
    try:
        v = float(val)
    except Exception:
        return None
    if v != v or v in (float('inf'), float('-inf')):  # NaN/inf
        return None
    # Unit handling:
    # - auto: legacy behavior (0..1 => scale by 100)
    # - fraction: explicitly treat as 0..1 and scale to percent
    # - percent: treat as already in percent (0..100), no scaling
    units = (value_units or "auto").lower()
    if units == "fraction":
        if 0.0 <= v <= 1.0:
            v *= 100.0
    elif units == "percent":
        pass  # keep as-is
    else:  # auto
        if 0.0 <= v <= 1.0:
            v *= 100.0
    # Clamp improbable values; log once
    if v < 0.0:
        print(f"⚠️  Accuracy < 0 encountered ({v}); clamping to 0.")
        v = 0.0
    if v > 100.0:
        print(f"⚠️  Accuracy > 100 encountered ({v}); clamping to 100.")
        v = 100.0
    return v

def _rec_key(row: Dict[str, Any]) -> Tuple:
    return tuple(row.get(k) for k in KEY_COLS)

def _add_to_agg(agg: Dict[Tuple, Dict[str, Any]], row: Dict[str, Any]):
    key = _rec_key(row)
    ns = int(row.get('num_samples', 0) or 0)
    acc = row.get('accuracy', None)
    tok = row.get('avg_tokens', None)

    if key not in agg:
        base = {k: row[k] for k in KEY_COLS}
        agg[key] = {
            **base,
            "_sum_samples": 0,         # total samples seen (for info)
            "_sum_acc_x_n": 0.0,
            "_sum_acc_samples": 0,     # denominator for accuracy
            "_sum_tok_x_n": 0.0,
            "_sum_tok_samples": 0,
        }

    # Always track total samples for context
    agg[key]["_sum_samples"] += ns

    # Only include accuracy/tokens in weighted averages if they exist
    if acc is not None:
        agg[key]["_sum_acc_x_n"] += float(acc) * ns
        agg[key]["_sum_acc_samples"] += ns
    if tok is not None:
        agg[key]["_sum_tok_x_n"] += float(tok) * ns
        agg[key]["_sum_tok_samples"] += ns

def _agg_to_rows(agg: Dict[Tuple, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for _, v in agg.items():
        n_total = int(v["_sum_samples"])
        avg_acc = round(v["_sum_acc_x_n"] / v["_sum_acc_samples"], 4) if v["_sum_acc_samples"] > 0 else ""
        avg_tok = round(v["_sum_tok_x_n"] / v["_sum_tok_samples"], 2) if v["_sum_tok_samples"] > 0 else ""
        rows.append({
            **{k: v[k] for k in KEY_COLS},
            'num_samples': n_total,
            'avg_tokens': avg_tok,
            'accuracy': avg_acc,
        })
    def _gs_numeric(gs_val):
        try:
            return int(gs_val)
        except Exception:
            m = re.search(r'(\d+)$', str(gs_val))
            return int(m.group(1)) if m else -1
    rows.sort(key=lambda r: (str(r['task']), str(r['model']), _gs_numeric(r['group_size']), str(r['truncated_budget'])))
    return rows

# ---------- AIME pivot helpers ----------
def _model_size_B(model_name: str) -> float:
    m = re.search(r'-([0-9.]+)[Bb]$', str(model_name))
    try: return float(m.group(1)) if m else -1.0
    except Exception: return -1.0

def _weight_prec_int(w: str) -> int:
    try: return int(w)
    except Exception: return -1

KV_PREC_COLS = [
    ("fp16", "fp16"),
    ("hqq_8", "HQQ-8b"),
    ("hqq_4", "HQQ-4b"),
    ("hqq_2", "HQQ-2b"),
]
KV_EVICT_COLS = [
    ("streamingllm_512_512","streaming 512+512"),
    ("streamingllm_1024_1024","1024+1024"),
    ("streamingllm_2048_2048","2048+2048"),
    ("streamingllm_4096_4096","4096+4096"),
    ("rkv_2048","rkv 2048"),
    ("rkv_4096","4096"),
    ("rkv_8192","8192"),
]
ORDERED_COLS = KV_PREC_COLS + KV_EVICT_COLS

def _normalize_kv_precision_key(raw: str) -> Optional[str]:
    s = (raw or "").lower()
    if s == "fp16": return "fp16"
    m = re.match(r"hqq[_-]?(\d+)", s)
    if m and m.group(1) in ("8","4","2"): return f"hqq_{m.group(1)}"
    return None

def _normalize_kv_eviction_key(raw: str) -> Optional[str]:
    s = (raw or "").lower()
    m = re.match(r"streamingllm[_-](\d+)[_-](\d+)", s)
    if m:
        k = f"streamingllm_{m.group(1)}_{m.group(2)}"
        return k if k in {x for x,_ in KV_EVICT_COLS} else None
    m = re.match(r"rkv[_-](\d+)", s)
    if m:
        k = f"rkv_{m.group(1)}"
        return k if k in {x for x,_ in KV_EVICT_COLS} else None
    return None

def _print_aime_pivot_combined(pivot_counts_by_task: Dict[str, Dict[Tuple[str, str], Dict[str, int]]]):
    rows_1 = set(pivot_counts_by_task.get("aime25_1", {} ).keys())
    rows_2 = set(pivot_counts_by_task.get("aime25_2", {} ).keys())
    row_keys = list(rows_1.union(rows_2))
    row_keys.sort(key=lambda rk: (-_model_size_B(rk[0]), -_weight_prec_int(rk[1]), rk[0]))

    cell_strings: Dict[Tuple[str, str], Dict[str, str]] = defaultdict(dict)
    for rk in row_keys:
        for key, _label in ORDERED_COLS:
            v1 = pivot_counts_by_task.get("aime25_1", {}).get(rk, {}).get(key, 0)
            v2 = pivot_counts_by_task.get("aime25_2", {}).get(rk, {}).get(key, 0)
            cell_strings[rk][key] = str(v1) if v1 == v2 else f"{v1} ({v2})"

    headers = ["model","w_prec"] + [label for _,label in ORDERED_COLS]
    widths = []
    widths.append(max(len("model"), max((len(rk[0]) for rk in row_keys), default=0)))
    widths.append(max(len("w_prec"), max((len(rk[1]) for rk in row_keys), default=0)))
    for key,label in ORDERED_COLS:
        widths.append(max(len(label), max((len(cell_strings[rk][key]) for rk in row_keys), default=1)))

    print("\nmodel       w_prec  " + "  ".join(h for h in [label for _,label in ORDERED_COLS]))
    print("-" * (sum(widths) + 2*(len(widths)-1)))
    for rk in row_keys:
        row_cells = [rk[0], rk[1]] + [cell_strings[rk][key] for key,_ in ORDERED_COLS]
        print("  ".join(c.ljust(w) for c,w in zip(row_cells, widths)))

# ---------- Main ----------
def main():
    parser = argparse.ArgumentParser(
        description="Collect & aggregate results (robust averages; skip non-ready serials).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--input_folders', nargs='+', required=True,
                        help="Root directories of experiments.")
    parser.add_argument('--output_file', required=True,
                        help="CSV path (rewritten each run).")
    parser.add_argument('--verbose', action='store_true', help="Print extra diagnostics.")
    parser.add_argument('--only_model_families', nargs='+', default=None,
                        help="Optional filter: only include records whose model family matches "
                             "any of these values (case-insensitive). Examples: Qwen DeepSeek OpenReasoning")
    parser.add_argument('--pass_at_k_units', choices=['auto','fraction','percent'], default='auto',
                        help="Units for pass_at_k values in summary.json. "
                             "'fraction' means 0..1 scaled to percent; "
                             "'percent' means already 0..100; "
                             "'auto' scales 0..1 by 100 (legacy behavior).")
    parser.add_argument('--only_prm', action='store_true',
                        help="Only include PRM best-of-N results; skip serial and majority rows.")
    args = parser.parse_args()

    print("🚀 Collecting (robust averaging; non-ready serials SKIPPED)...")

    agg: Dict[Tuple, Dict[str, Any]] = {}
    mj_pat = re.compile(r"majority_vote_g(\d+)_t(\d+)_results\.json")
    prm_pat = re.compile(r"prm_bestof_g(\d+)_t(\d+)_results\.json")

    # AIME counts: pivot_counts_by_task[task][(model,w_prec)][col_key] = n
    pivot_counts_by_task: Dict[str, Dict[Tuple[str, str], Dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    pivot_seen: Set[Tuple[str, str, str, str, str]] = set()

    # Cohorts flagged if ANY truncate is not-ready
    missing_by_task: Dict[str, Set[str]] = defaultdict(set)

    only_fams: Set[str] = set(f.lower() for f in (args.only_model_families or []))

    for folder in args.input_folders:
        if not os.path.isdir(folder):
            print(f"⚠️  '{folder}' is not a directory. Skipping.")
            continue

        for root, _, _ in os.walk(folder):
            if not os.path.basename(root).startswith('truncate_'):
                continue

            summary_path = os.path.join(root, 'summary.json')
            if not os.path.exists(summary_path):
                print(f"⚠️  No summary.json in {root}, skipping.")
                continue

            try:
                with open(summary_path, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)

                cfg = summary_data.get('configuration', {}) or {}
                task_name = (cfg.get('task', {}) or {}).get('name') or ""
                avg_tokens = (summary_data.get('avg_prompt_tokens', 0) or 0) + (summary_data.get('avg_completion_tokens', 0) or 0)
                cohort_root = os.path.abspath(os.path.dirname(root))
                n_samples = _extract_num_samples(summary_data, source_hint=summary_path)

                # ---- Optional model family filter ----
                model_name = extract_model_name(cfg)
                if only_fams:
                    fam = _infer_model_family_from_name(model_name)
                    if fam is None or fam.lower() not in only_fams:
                        continue

                # ---- SERIAL readiness (non-zero); SKIP from aggregation if not ready ----
                if not args.only_prm:
                    serial_ready = serial_is_ready_nonzero(summary_data)
                    if not serial_ready:
                        missing_by_task[task_name].add(os.path.relpath(cohort_root))
                        if args.verbose:
                            print(f"⏭️  Skipping non-ready serial @ {root}")
                    else:
                        # serial accuracy (prefer k=1; else accuracy)
                        pak = summary_data.get('pass_at_k')
                        acc_field = summary_data.get('accuracy')
                        if acc_field is not None:
                            acc_val = acc_field
                            acc_units = "auto"   # assume accuracy is already in a consistent unit
                        else:
                            acc_val = pak.get('k=1') if isinstance(pak, dict) else None
                            acc_units = args.pass_at_k_units
                        acc_serial = _normalize_accuracy_to_pct(acc_val, acc_units)

                        kv_precision = compute_kv_precision(cfg)
                        kv_eviction = compute_kv_eviction(cfg, run_root=cohort_root)

                        base = {
                            'task': task_name,
                            'model': extract_model_name(cfg),
                            'weight_precision': determine_weight_precision(cfg),
                            'weight_quant': determine_weight_quant_scheme(cfg),
                            'kv_precision': kv_precision,
                            'kv_eviction': kv_eviction,
                            'truncated_budget': cfg.get('truncated_budget'),
                            'avg_tokens': round(float(avg_tokens), 2),
                        }

                        # SERIAL row (g=1)
                        _add_to_agg(agg, {
                            **base,
                            'group_size': 1,
                            'num_samples': int(n_samples),
                            'accuracy': acc_serial,
                        })

                        # AIME pivot counts (only for ready serials)
                        if task_name in {"aime25_1", "aime25_2"}:
                            impl, _, _ = _get_cache_impl_and_cfg(cfg)
                            internal_prec = _normalize_kv_precision_key(kv_precision)
                            internal_evict = _normalize_kv_eviction_key(kv_eviction)
                            chosen = None
                            if impl == "quantized" and internal_prec:
                                chosen = internal_prec
                            elif impl in {"streamingllm", "rkv"} and internal_evict:
                                chosen = internal_evict
                            elif internal_prec:
                                chosen = internal_prec
                            if chosen:
                                pv_key = (task_name, cohort_root, base['model'], base['weight_precision'], chosen)
                                if pv_key not in pivot_seen:
                                    pivot_seen.add(pv_key)
                                    pivot_counts_by_task[task_name][(base['model'], base['weight_precision'])][chosen] += int(n_samples)

            except Exception as e:
                print(f"❌ Error processing {summary_path}: {e}. Skipping.")
                continue

            # ---- Majority vote in same truncate dir (only include if overall_accuracy present) ----
            if not args.only_prm:
                for p in Path(root).glob("majority_vote_g*_t*_results.json"):
                    m = mj_pat.match(p.name)
                    if not m: continue
                    g, _t = map(int, m.groups())
                    try:
                        with open(p, 'r', encoding='utf-8') as f:
                            mj = json.load(f)
                        if 'overall_accuracy' not in mj or mj['overall_accuracy'] is None:
                            missing_by_task[task_name].add(os.path.relpath(cohort_root))
                            if args.verbose:
                                print(f"⏭️  Skipping MV (no overall_accuracy) @ {p}")
                            continue

                        kv_precision = compute_kv_precision(cfg)
                        kv_eviction = compute_kv_eviction(cfg, run_root=cohort_root)
                        base = {
                            'task': task_name,
                            'model': extract_model_name(cfg),
                            'weight_precision': determine_weight_precision(cfg),
                            'weight_quant': determine_weight_quant_scheme(cfg),
                            'kv_precision': kv_precision,
                            'kv_eviction': kv_eviction,
                            'truncated_budget': cfg.get('truncated_budget'),
                            'avg_tokens': round(float(avg_tokens), 2),
                        }
                        _add_to_agg(agg, {
                            **base,
                            'group_size': g,
                            'num_samples': int(n_samples),
                            'accuracy': _normalize_accuracy_to_pct(mj.get('overall_accuracy'), "auto"),
                        })
                    except Exception as e:
                        print(f"❌ Error processing {p}: {e}")

            # ---- PRM best-of-N results in same truncate dir ----
            for p in Path(root).glob("prm_bestof_g*_t*_results.json"):
                m = prm_pat.match(p.name)
                if not m: continue
                g, _t = map(int, m.groups())
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        po = json.load(f)
                    if 'overall_accuracy' not in po or po['overall_accuracy'] is None:
                        missing_by_task[task_name].add(os.path.relpath(cohort_root))
                        if args.verbose:
                            print(f"⏭️  Skipping PRM (no overall_accuracy) @ {p}")
                        continue

                    kv_precision = compute_kv_precision(cfg)
                    kv_eviction = compute_kv_eviction(cfg, run_root=cohort_root)
                    base = {
                        'task': task_name,
                        'model': extract_model_name(cfg),
                        'weight_precision': determine_weight_precision(cfg),
                        'weight_quant': determine_weight_quant_scheme(cfg),
                        'kv_precision': kv_precision,
                        'kv_eviction': kv_eviction,
                        'truncated_budget': cfg.get('truncated_budget'),
                        'avg_tokens': round(float(avg_tokens), 2),
                    }
                    _add_to_agg(agg, {
                        **base,
                        # Tag PRM results in group_size to avoid colliding with majority rows, e.g., "prm_4"
                        'group_size': f"prm_{g}",
                        'num_samples': int(n_samples),
                        'accuracy': _normalize_accuracy_to_pct(po.get('overall_accuracy'), "auto"),
                    })
                except Exception as e:
                    print(f"❌ Error processing {p}: {e}")

    # ----- Write CSV -----
    if not agg:
        print("✅ No ready records found.")
        _print_missing_dirs_sorted(missing_by_task)
        return

    rows = _agg_to_rows(agg)
    try:
        with open(args.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=HEADER)
            writer.writeheader(); writer.writerows(rows)
        print(f"💾 Wrote {len(rows)} aggregated rows to '{args.output_file}'.")
    except IOError as e:
        print(f"❌ Could not write '{args.output_file}': {e}")
        _print_missing_dirs_sorted(missing_by_task)
        return

    # ----- AIME pivot & missing list -----
    _print_aime_pivot_combined(pivot_counts_by_task)
    _print_missing_dirs_sorted(missing_by_task)

def _print_missing_dirs_sorted(missing_by_task: Dict[str, Set[str]]):
    preferred = ['aime25_1','aime25_2']
    other = sorted([t for t in missing_by_task if t not in preferred])
    order = [t for t in preferred if t in missing_by_task] + other

    print("\n# Directories with missing/ not-ready (sorted by task)")
    print("BASE_DIRS=(")
    for t in order:
        for d in sorted(missing_by_task[t]):
            print(f'  "{d}"')
    print(")")

if __name__ == "__main__":
    main()
