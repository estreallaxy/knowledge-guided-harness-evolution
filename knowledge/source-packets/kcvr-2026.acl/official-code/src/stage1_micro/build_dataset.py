from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.stage1_micro.plan_utils import PlanSerializeConfig, build_micro_prompt, serialize_plan  # noqa: E402
from src.utils.video_utils import subject_order  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _load_id_maps(nodes_kc_csv: Path, nodes_tp_csv: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Load id->name maps from aggregated KG csvs.

    Args:
        nodes_kc_csv: knowledge_graph/raw_csv/nodes_kc.csv
        nodes_tp_csv: knowledge_graph/raw_csv/nodes_tp.csv

    Returns:
        (id2kc, id2tp)
    """
    import csv

    id2kc: Dict[str, str] = {}
    with nodes_kc_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = (row.get("id") or "").strip()
            name = (row.get("name") or "").strip()
            if rid and name:
                id2kc[rid] = name

    id2tp: Dict[str, str] = {}
    with nodes_tp_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = (row.get("id") or "").strip()
            name = (row.get("name") or "").strip()
            if rid and name:
                id2tp[rid] = name

    return id2kc, id2tp


def _find_plan(plans_root: Path, subject: str, video_id: str, segment_id: str) -> Optional[Path]:
    plan_id = f"{video_id}__{segment_id}"
    p = plans_root / subject / video_id / f"{plan_id}.json"
    return p if p.exists() else None


def _build_output(objectives_gt: Sequence[str], summary_gt: str) -> str:
    """Build supervised output text (structured).

    Args:
        objectives_gt: List of learning objectives.
        summary_gt: Structured summary target.

    Returns:
        Output string.
    """
    obj = "\n".join([str(x) for x in objectives_gt if str(x).strip()])
    return f"### 学习目标\n{obj}\n\n### 结构化摘要\n{summary_gt}".strip() + "\n"


def build_micro_sft_dataset(
    std_micro_root: Path,
    plans_root: Path,
    kg_raw_csv_root: Path,
    out_jsonl: Path,
    subjects: Sequence[str],
    plan_cfg: PlanSerializeConfig,
) -> Tuple[int, List[str]]:
    """Build micro SFT dataset for LLaMA-Factory (mllm sharegpt format).

    Output schema (one sample):
    {
      "messages": [{"role":"user","content":"<image>...prompt"}, {"role":"assistant","content":"..."}],
      "images": [".../000.jpg", ..., ".../007.jpg"]
    }

    Args:
        std_micro_root: data/annotations/standard_labels/micro
        plans_root: cache/plans/micro_plans
        kg_raw_csv_root: knowledge_graph/raw_csv
        out_jsonl: trainsets/micro_sft_v1.jsonl
        subjects: Subjects.
        plan_cfg: Serialization config.

    Returns:
        (count, issues)
    """
    id2kc, id2tp = _load_id_maps(kg_raw_csv_root / "nodes_kc.csv", kg_raw_csv_root / "nodes_tp.csv")
    issues: List[str] = []
    samples: List[Dict[str, Any]] = []

    for subject in subjects:
        subj_dir = std_micro_root / subject
        if not subj_dir.exists():
            continue
        for seg_path in sorted(subj_dir.rglob("*.json")):
            seg = _read_json(seg_path)
            video_id = str(seg.get("video_id", "") or "")
            segment_id = str(seg.get("segment_id", "") or "")
            stage = str(seg.get("stage", "") or "")
            images = seg.get("image_paths") or []
            transcript = str(seg.get("text_input", "") or "")
            objectives_gt = seg.get("objectives_gt") or []
            summary_gt = str(seg.get("summary_gt", "") or "")

            if not video_id or not segment_id or not stage:
                issues.append(f"{seg_path}:missing_video_or_segment_or_stage")
                continue
            if not isinstance(images, list) or len(images) != 8:
                issues.append(f"{seg_path}:bad_image_paths:{len(images) if isinstance(images, list) else 'NA'}")
                continue

            plan_path = _find_plan(plans_root, subject, video_id, segment_id)
            if plan_path is None:
                issues.append(f"{seg_path}:missing_plan:{subject}/{video_id}/{segment_id}")
                continue
            plan = _read_json(plan_path)

            plan_text = serialize_plan(plan, id2kc=id2kc, id2tp=id2tp, cfg=plan_cfg)
            prompt, _ = build_micro_prompt(stage=stage, plan_text=plan_text, transcript=transcript, num_images=len(images))
            output = _build_output(objectives_gt=objectives_gt, summary_gt=summary_gt)

            samples.append(
                {
                    "messages": [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": output},
                    ],
                    "images": images,
                    "meta": {
                        "subject": subject,
                        "video_id": video_id,
                        "segment_id": segment_id,
                        "stage": stage,
                        "source_seg_path": seg_path.as_posix(),
                        "source_plan_path": plan_path.as_posix(),
                    },
                }
            )

    _write_jsonl(out_jsonl, samples)
    return len(samples), issues


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build KCVR micro SFT dataset (LLaMA-Factory mllm sharegpt format).")
    p.add_argument("--std-micro-root", type=Path, default=Path("data/annotations/standard_labels/micro"))
    p.add_argument("--plans-root", type=Path, default=Path("cache/plans/micro_plans"))
    p.add_argument("--kg-raw-csv-root", type=Path, default=Path("knowledge_graph/raw_csv"))
    p.add_argument("--out-jsonl", type=Path, default=Path("trainsets/micro_sft_v1.jsonl"))
    p.add_argument("--subjects", type=str, nargs="*", default=None)
    p.add_argument("--max-tp-anchors", type=int, default=2)
    p.add_argument("--max-kc-concepts", type=int, default=12)
    p.add_argument("--max-deps", type=int, default=5)
    p.add_argument("--report", type=Path, default=Path("experiments/v7.4_run1/micro_sft_build_issues.txt"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    subs = args.subjects or subject_order()
    cfg = PlanSerializeConfig(
        max_tp_anchors=args.max_tp_anchors,
        max_kc_concepts=args.max_kc_concepts,
        max_deps=args.max_deps,
    )
    n, issues = build_micro_sft_dataset(
        std_micro_root=args.std_micro_root,
        plans_root=args.plans_root,
        kg_raw_csv_root=args.kg_raw_csv_root,
        out_jsonl=args.out_jsonl,
        subjects=subs,
        plan_cfg=cfg,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    # Write a human-readable report even when there are no issues (avoid confusing empty file).
    summary = [
        f"micro_samples={n}",
        f"issues={len(issues)}",
        f"out={args.out_jsonl}",
    ]
    body = "\n".join(summary + ([""] + issues if issues else ["", "OK"]))
    args.report.write_text(body + "\n", encoding="utf-8")
    print(f"micro_samples={n} issues={len(issues)} out={args.out_jsonl} report={args.report}")


if __name__ == "__main__":
    main()


