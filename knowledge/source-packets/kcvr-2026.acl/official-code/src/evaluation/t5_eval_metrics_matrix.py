"""
T5: 指标验证矩阵评测（GT / ASR / 劣化 baseline）
=============================================

输入：
- standard_labels (micro): summary_plain, objectives_plain
- raw_labels (segments): summary_micro_asr
- plans (micro_plans): pi_kc, edges_based_on, edges_next
- degraded jsonl: 来自 t5_generate_degraded_baselines.py

输出：
- per-sample CSV（含 KPC 诊断字段）
- per-variant summary.txt（按 subject & overall）

关键：此脚本的目的不是“强行让 GT > ASR”，而是验证指标对劣化是否敏感：
- kpc_reverse: KPC 应显著下降
- loc_drop: LOC 应显著下降
- shuffle: KPC/LOC 应有一定下降（但幅度可能更小）

用法（20 样本小验证，默认跳过 BS 加速）：
  conda run -n ljj_dev python src/evaluation/t5_eval_metrics_matrix.py \
    --labels-root data/annotations/standard_labels/micro \
    --raw-labels-root data/annotations/raw_labels/segments \
    --plans-root cache/plans/micro_plans \
    --kg-csv-root knowledge_graph/raw_csv \
    --alias-root knowledge_graph/alias \
    --subjects biology chemistry \
    --max-samples-per-subject 10 \
    --degraded-jsonl experiments/v7.4_run1/t5_matrix/degraded.jsonl \
    --output-dir experiments/v7.4_run1/t5_matrix \
    --skip-bs
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure repo root on sys.path so `src.*` imports work when executed as a script.
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.utils.metric_utils import (
    CtlResources,
    clean_text_for_eval,
    compute_concept_f1,
    compute_kpc,
    compute_loc,
    compute_rouge,
    triggered_concepts,
)


def _load_json(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_ctl_resources(kg_csv_root: Path, alias_root: Path, subjects: List[str]) -> CtlResources:
    kc_dict: Dict[str, str] = {}
    kc_csv = kg_csv_root / "nodes_kc.csv"
    with open(kc_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kc_id = (row.get("id") or "").strip()
            name = (row.get("name") or "").strip()
            if kc_id and name:
                kc_dict[kc_id] = name

    kc_synonyms: Dict[str, List[str]] = {}
    for subject in subjects:
        alias_file = alias_root / f"{subject}_alias.json"
        if not alias_file.exists():
            continue
        alias_data = _load_json(alias_file)
        for kc_id, info in alias_data.items():
            kc_synonyms.setdefault(kc_id, []).extend(info.get("aliases", []))

    return CtlResources(kc_dict=kc_dict, kc_synonyms=kc_synonyms, trie=None, normalizer=None)


def _objectives_text(std_label: Dict) -> str:
    obj = std_label.get("objectives_plain") or std_label.get("objectives_gt") or std_label.get("learning_objectives") or ""
    if isinstance(obj, list):
        obj = "\n".join(str(x) for x in obj)
    return clean_text_for_eval(str(obj))


def _gt_summary(std_label: Dict) -> str:
    return clean_text_for_eval((std_label.get("summary_plain") or std_label.get("summary_gt") or "").strip())


def _asr_summary(raw_label: Optional[Dict]) -> str:
    if not raw_label:
        return ""
    return clean_text_for_eval((raw_label.get("summary_micro_asr") or "").strip())


def _stage_to_seg(stage: str) -> Optional[str]:
    return {
        "intro": "seg_0001",
        "exposition": "seg_0002",
        "interaction": "seg_0003",
        "conclusion": "seg_0004",
    }.get(stage)


def _kpc_diagnostics(
    pred_text: str,
    subject: str,
    ctl: CtlResources,
    plan_pi_kc: List[str],
    edges_based_on: List[Tuple[str, str]],
    edges_next: List[Tuple[str, str]],
) -> Dict[str, float]:
    """
    Mirror compute_kpc core accounting to explain why KPC is high/low.
    """
    pred_text = clean_text_for_eval(pred_text)
    pred_concepts = triggered_concepts(pred_text, subject, ctl)
    pred_order = {c.kc_id: c.first_pos for c in pred_concepts}
    pi_set = set(plan_pi_kc or [])

    based_w, next_w = 1.0, 0.5
    total_w = 0.0
    bad_w = 0.0
    verifiable_edges = 0
    violations = 0

    def acc(edges: List[Tuple[str, str]], w: float) -> None:
        nonlocal total_w, bad_w, verifiable_edges, violations
        for u, v in edges:
            if pi_set and (u not in pi_set or v not in pi_set):
                continue
            if u in pred_order and v in pred_order:
                verifiable_edges += 1
                total_w += w
                if pred_order[u] > pred_order[v]:
                    violations += 1
                    bad_w += w

    acc(edges_based_on or [], based_w)
    acc(edges_next or [], next_w)
    return {
        "triggered_kc": float(len(pred_order)),
        "verifiable_edges": float(verifiable_edges),
        "kpc_total_w": float(total_w),
        "kpc_bad_w": float(bad_w),
        "kpc_violation_rate": float((bad_w / total_w) if total_w > 0 else 0.0),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-root", required=True)
    parser.add_argument("--raw-labels-root", required=True)
    parser.add_argument("--plans-root", required=True)
    parser.add_argument("--kg-csv-root", required=True)
    parser.add_argument("--alias-root", required=True)
    parser.add_argument("--subjects", nargs="+", required=True)
    parser.add_argument("--max-samples-per-subject", type=int, default=10)
    parser.add_argument("--degraded-jsonl", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--skip-bs", action="store_true")
    args = parser.parse_args()

    labels_root = Path(args.labels_root)
    raw_labels_root = Path(args.raw_labels_root)
    plans_root = Path(args.plans_root)
    kg_csv_root = Path(args.kg_csv_root)
    alias_root = Path(args.alias_root)
    degraded_jsonl = Path(args.degraded_jsonl)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ctl = _build_ctl_resources(kg_csv_root, alias_root, args.subjects)

    # load degraded map: (subject, video_id, segment_id) -> {variant: text}
    degraded_map: Dict[Tuple[str, str, str], Dict[str, str]] = defaultdict(dict)
    with open(degraded_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            key = (obj["subject"], obj["video_id"], obj["segment_id"])
            degraded_map[key][obj["variant"]] = obj["pred_text"]

    # candidates per sample
    variants = ["gt", "asr", "kpc_reverse", "loc_drop", "shuffle"]

    rows = []
    by_subject_variant: Dict[Tuple[str, str], List[Dict[str, float]]] = defaultdict(list)
    by_variant: Dict[str, List[Dict[str, float]]] = defaultdict(list)

    for subject in args.subjects:
        subj_labels_root = labels_root / subject
        subj_raw_root = raw_labels_root / subject
        subj_plans_root = plans_root / subject
        n = 0
        for video_dir in sorted(subj_labels_root.iterdir()):
            if not video_dir.is_dir():
                continue
            video_prefix = video_dir.name
            for label_file in sorted(video_dir.glob("*.json")):
                if n >= args.max_samples_per_subject:
                    break
                parts = label_file.stem.split("_")
                if len(parts) < 3:
                    continue
                video_id = f"{parts[0]}_{parts[1]}"
                stage = parts[2]
                seg_id = _stage_to_seg(stage)
                if not seg_id:
                    continue

                std_label = _load_json(label_file)
                raw_path = subj_raw_root / video_prefix / label_file.name
                raw_label = _load_json(raw_path) if raw_path.exists() else None
                plan_path = subj_plans_root / video_id / f"{video_id}__{seg_id}.json"
                if not plan_path.exists():
                    continue
                plan = _load_json(plan_path)

                gt_sum = _gt_summary(std_label)
                if not gt_sum:
                    continue
                asr_sum = _asr_summary(raw_label)
                obj_text = _objectives_text(std_label)

                plan_pi = plan.get("pi_kc") or plan.get("pi") or []
                edges_based_on = plan.get("edges_based_on") or []
                edges_next = plan.get("edges_next") or []

                key = (subject, video_id, seg_id)
                deg = degraded_map.get(key, {})

                cand_texts = {
                    "gt": gt_sum,
                    "asr": asr_sum,
                    "kpc_reverse": deg.get("kpc_reverse", ""),
                    "loc_drop": deg.get("loc_drop", ""),
                    "shuffle": deg.get("shuffle", ""),
                }

                # Evaluate each variant
                for v in variants:
                    pred = cand_texts.get(v, "")
                    if not pred:
                        continue
                    rouge = compute_rouge(pred, gt_sum)
                    bs = None
                    if not args.skip_bs:
                        # optional: heavy, allow user to rerun without skip
                        from src.utils.metric_utils import compute_bertscore

                        bs = compute_bertscore(pred, gt_sum)
                    cf1 = compute_concept_f1(pred, gt_sum, subject, ctl)["C-F1"]
                    kpc = compute_kpc(pred, plan_pi, edges_based_on, edges_next, subject, ctl)
                    loc = compute_loc(pred, obj_text)
                    diag = _kpc_diagnostics(pred, subject, ctl, plan_pi, edges_based_on, edges_next)

                    row = {
                        "subject": subject,
                        "video_id": video_id,
                        "segment_id": seg_id,
                        "stage": stage,
                        "variant": v,
                        "R1": rouge["R1"],
                        "R2": rouge["R2"],
                        "RL": rouge["RL"],
                        "BS": (bs if bs is not None else ""),
                        "C-F1": cf1,
                        "KPC": kpc,
                        "LOC": loc,
                        **diag,
                    }
                    rows.append(row)
                    metric_pack = {"R1": rouge["R1"], "R2": rouge["R2"], "RL": rouge["RL"], "C-F1": cf1, "KPC": kpc, "LOC": loc}
                    by_subject_variant[(subject, v)].append(metric_pack)
                    by_variant[v].append(metric_pack)

                n += 1
            if n >= args.max_samples_per_subject:
                break

    # Write CSV
    out_csv = output_dir / "t5_matrix_detailed.csv"
    fieldnames = ["subject", "video_id", "segment_id", "stage", "variant", "R1", "R2", "RL", "BS", "C-F1", "KPC", "LOC", "triggered_kc", "verifiable_edges", "kpc_total_w", "kpc_bad_w", "kpc_violation_rate"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            # ensure all fields exist
            for k in fieldnames:
                r.setdefault(k, "")
            w.writerow(r)

    # Summaries
    def mean(xs: List[float]) -> float:
        return sum(xs) / len(xs) if xs else 0.0

    def summarize(packs: List[Dict[str, float]]) -> Dict[str, float]:
        return {
            "R1": mean([p["R1"] for p in packs]),
            "R2": mean([p["R2"] for p in packs]),
            "RL": mean([p["RL"] for p in packs]),
            "C-F1": mean([p["C-F1"] for p in packs]),
            "KPC": mean([p["KPC"] for p in packs]),
            "LOC": mean([p["LOC"] for p in packs]),
        }

    lines = []
    lines.append("=" * 90)
    lines.append("T5 Metrics Validation Matrix (GT / ASR / Degraded)")
    lines.append("=" * 90)
    lines.append(f"subjects={args.subjects}, max_samples_per_subject={args.max_samples_per_subject}, skip_bs={args.skip_bs}")
    lines.append(f"degraded_jsonl={degraded_jsonl}")
    lines.append("")

    # per subject
    for subject in args.subjects:
        lines.append(f"[{subject.upper()}]")
        for v in variants:
            packs = by_subject_variant.get((subject, v), [])
            if not packs:
                continue
            s = summarize(packs)
            lines.append(f"  {v:12s} n={len(packs):3d} | KPC={s['KPC']:.4f} LOC={s['LOC']:.4f} C-F1={s['C-F1']:.4f} | R1={s['R1']:.4f} R2={s['R2']:.4f} RL={s['RL']:.4f}")
        lines.append("")

    # overall
    lines.append("[OVERALL]")
    for v in variants:
        packs = by_variant.get(v, [])
        if not packs:
            continue
        s = summarize(packs)
        lines.append(f"  {v:12s} n={len(packs):3d} | KPC={s['KPC']:.4f} LOC={s['LOC']:.4f} C-F1={s['C-F1']:.4f} | R1={s['R1']:.4f} R2={s['R2']:.4f} RL={s['RL']:.4f}")
    lines.append("")
    lines.append("Expected sensitivity (heuristic):")
    lines.append("- kpc_reverse: KPC should drop noticeably vs asr/gt")
    lines.append("- loc_drop: LOC should drop noticeably vs asr/gt")
    lines.append("- shuffle: KPC/LOC may drop moderately")
    lines.append("=" * 90)

    out_txt = output_dir / "t5_matrix_summary.txt"
    out_txt.write_text("\n".join(lines), encoding="utf-8")

    print(f"✅ Wrote: {out_csv}")
    print(f"✅ Wrote: {out_txt}")
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()


