"""
T5: 生成劣化 baseline（GT/ASR/劣化）用于指标有效性验证
=========================================================

目标（KCVR 指标“有效性”）：
- KPC 应对“顺序倒置”敏感（KPC 显著下降）
- LOC 应对“目标缺失”敏感（LOC 显著下降）

本脚本负责生成“劣化预测文本”，写出 jsonl，供后续评测脚本读取。

生成的劣化策略（v1）：
1) kpc_reverse: 显式按 π 的反序列出概念（强制打乱递进顺序）
2) loc_drop: 仅保留“教师动作/课堂组织”叙事，刻意回避知识点与目标关键词
3) shuffle: 将 GT 摘要按句子打乱顺序（弱化局部递进）

输出 jsonl schema:
{
  "subject": "...",
  "video_id": "...",
  "segment_id": "seg_0001",
  "stage": "intro",
  "variant": "kpc_reverse|loc_drop|shuffle",
  "pred_text": "..."
}

用法（20 样本小验证，建议先跳过 BS，加快速度）：
  conda run -n ljj_dev python src/evaluation/t5_generate_degraded_baselines.py \
    --labels-root data/annotations/standard_labels/micro \
    --raw-labels-root data/annotations/raw_labels/segments \
    --plans-root cache/plans/micro_plans \
    --kg-csv-root knowledge_graph/raw_csv \
    --subjects biology chemistry \
    --max-samples-per-subject 10 \
    --out-jsonl experiments/v7.4_run1/t5_matrix/degraded.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _load_json(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_kc_dict(kg_csv_root: Path) -> Dict[str, str]:
    kc_path = kg_csv_root / "nodes_kc.csv"
    kc_dict: Dict[str, str] = {}
    with open(kc_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kc_id = (row.get("id") or "").strip()
            name = (row.get("name") or "").strip()
            if kc_id and name:
                kc_dict[kc_id] = name
    return kc_dict


def _split_sentences_zh(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    # keep punctuation as separators; simple heuristic is enough for degradation
    parts = re.split(r"[。！？!\?]\s*", text)
    sents = [p.strip() for p in parts if p.strip()]
    return sents


def _variant_kpc_reverse(plan: Dict, kc_dict: Dict[str, str]) -> str:
    pi = plan.get("pi_kc") or plan.get("pi") or []
    names = [kc_dict.get(k, k) for k in pi]
    names = [n for n in names if n]
    if not names:
        return "本段知识递进（故意颠倒）：无。"
    # limit to reduce noise / avoid extremely long texts
    names = list(reversed(names[:10]))
    return "本段知识递进（故意颠倒顺序）：{}。".format(" → ".join(names))


def _variant_loc_drop() -> str:
    # Intentionally content-weak, action-heavy narrative; should reduce LOC.
    return (
        "教师在黑板书写并指向屏幕，组织学生观察、提问与讨论，"
        "通过举例与互动帮助学生梳理思路并完成课堂小结。"
    )


def _variant_shuffle(gt_summary_plain: str, seed: int) -> str:
    sents = _split_sentences_zh(gt_summary_plain)
    if len(sents) <= 1:
        return gt_summary_plain.strip()
    rng = random.Random(seed)
    rng.shuffle(sents)
    return "。".join(sents) + "。"


def _iter_samples(
    subject: str,
    labels_root: Path,
    raw_labels_root: Path,
    plans_root: Path,
    max_samples: int,
) -> List[Tuple[Dict, Optional[Dict], Dict]]:
    """
    Returns list of (std_label, raw_label, plan) for samples.
    """
    out: List[Tuple[Dict, Optional[Dict], Dict]] = []
    subj_labels_root = labels_root / subject
    subj_raw_root = raw_labels_root / subject
    subj_plans_root = plans_root / subject

    stage_to_seg = {
        "intro": "seg_0001",
        "exposition": "seg_0002",
        "interaction": "seg_0003",
        "conclusion": "seg_0004",
    }

    for video_dir in sorted(subj_labels_root.iterdir()):
        if not video_dir.is_dir():
            continue
        video_prefix = video_dir.name  # "001"
        for label_file in sorted(video_dir.glob("*.json")):
            if len(out) >= max_samples:
                return out
            parts = label_file.stem.split("_")
            if len(parts) < 3:
                continue
            video_id = f"{parts[0]}_{parts[1]}"
            stage = parts[2]
            seg_id = stage_to_seg.get(stage)
            if not seg_id:
                continue

            std_label = _load_json(label_file)
            # raw label optional
            raw_path = subj_raw_root / video_prefix / label_file.name
            raw_label = _load_json(raw_path) if raw_path.exists() else None

            plan_path = subj_plans_root / video_id / f"{video_id}__{seg_id}.json"
            if not plan_path.exists():
                continue
            plan = _load_json(plan_path)
            out.append((std_label, raw_label, plan))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-root", required=True)
    parser.add_argument("--raw-labels-root", required=True)
    parser.add_argument("--plans-root", required=True)
    parser.add_argument("--kg-csv-root", required=True)
    parser.add_argument("--subjects", nargs="+", required=True)
    parser.add_argument("--max-samples-per-subject", type=int, default=10)
    parser.add_argument("--out-jsonl", required=True)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    labels_root = Path(args.labels_root)
    raw_labels_root = Path(args.raw_labels_root)
    plans_root = Path(args.plans_root)
    kg_csv_root = Path(args.kg_csv_root)
    out_jsonl = Path(args.out_jsonl)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    kc_dict = _load_kc_dict(kg_csv_root)

    rows = []
    for subject in args.subjects:
        samples = _iter_samples(
            subject=subject,
            labels_root=labels_root,
            raw_labels_root=raw_labels_root,
            plans_root=plans_root,
            max_samples=args.max_samples_per_subject,
        )
        for std_label, _raw_label, plan in samples:
            video_id = plan.get("video_id") or std_label.get("video_id") or ""
            segment_id = plan.get("segment_id") or std_label.get("segment_id") or ""
            stage = plan.get("stage") or std_label.get("stage") or ""

            gt_summary_plain = (std_label.get("summary_plain") or std_label.get("summary_gt") or "").strip()

            rows.append(
                {
                    "subject": subject,
                    "video_id": video_id,
                    "segment_id": segment_id,
                    "stage": stage,
                    "variant": "kpc_reverse",
                    "pred_text": _variant_kpc_reverse(plan, kc_dict),
                }
            )
            rows.append(
                {
                    "subject": subject,
                    "video_id": video_id,
                    "segment_id": segment_id,
                    "stage": stage,
                    "variant": "loc_drop",
                    "pred_text": _variant_loc_drop(),
                }
            )
            rows.append(
                {
                    "subject": subject,
                    "video_id": video_id,
                    "segment_id": segment_id,
                    "stage": stage,
                    "variant": "shuffle",
                    "pred_text": _variant_shuffle(gt_summary_plain, seed=args.seed),
                }
            )

    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"✅ Wrote {len(rows)} degraded samples to: {out_jsonl}")


if __name__ == "__main__":
    main()



