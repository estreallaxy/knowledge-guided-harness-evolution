import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.stage1_micro.plan_utils import PlanSerializeConfig, serialize_plan
from src.utils.video_utils import subject_order

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _load_id_maps(nodes_kc_csv: Path, nodes_tp_csv: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
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


def _seg_stage_order(stage: str) -> int:
    return {"intro": 1, "exposition": 2, "interaction": 3, "conclusion": 4}.get(stage, 99)


def _find_micro_seg(std_micro_root: Path, subject: str, video_dir: str, stage: str) -> Optional[Path]:
    p = std_micro_root / subject / video_dir / f"{subject}_{video_dir}_{stage}.json"
    return p if p.exists() else None


def _find_plan(plans_root: Path, subject: str, video_id: str, segment_id: str) -> Optional[Path]:
    plan_id = f"{video_id}__{segment_id}"
    p = plans_root / subject / video_id / f"{plan_id}.json"
    return p if p.exists() else None


def _build_gks_text(plan_texts: List[str]) -> str:
    # Build GKS text from segment plans
    parts = ["[全课骨架 GKS]"]
    for i, txt in enumerate(plan_texts, start=1):
        parts.append(f"\n--- Segment {i} Plan ---\n{txt}")
    return "\n".join(parts).strip() + "\n"


def build_macro_sft_teacher_forcing(
    std_micro_root: Path,
    std_macro_root: Path,
    plans_root: Path,
    kg_raw_csv_root: Path,
    out_edu_jsonl: Path,
    out_overall_jsonl: Path,
    subjects: Sequence[str],
    plan_cfg: PlanSerializeConfig,
) -> Tuple[Tuple[int, int], List[str]]:
    # Build macro fusion SFT dataset using GT micro summaries (teacher forcing).
    id2kc, id2tp = _load_id_maps(kg_raw_csv_root / "nodes_kc.csv", kg_raw_csv_root / "nodes_tp.csv")
    issues: List[str] = []
    edu_rows: List[Dict[str, Any]] = []
    overall_rows: List[Dict[str, Any]] = []

    for subject in subjects:
        subj_macro = std_macro_root / subject
        if not subj_macro.exists():
            continue
        for video_dir_path in sorted([p for p in subj_macro.rglob("*_global.json") if p.is_file()]):
            macro = _read_json(video_dir_path)
            video_dir = str(macro.get("video_dir", "") or video_dir_path.parent.name)
            video_id = str(macro.get("video_id", "") or f"{subject}_{video_dir}")

            # Load 4 micro segments (GT)
            segs: List[Dict[str, Any]] = []
            plan_texts: List[str] = []
            seg_summaries: List[str] = []

            for stage in ["intro", "exposition", "interaction", "conclusion"]:
                seg_path = _find_micro_seg(std_micro_root, subject, video_dir, stage)
                if seg_path is None:
                    issues.append(f"{subject}/{video_dir}:missing_micro:{stage}")
                    segs = []
                    break
                seg = _read_json(seg_path)
                segs.append(seg)
                seg_summaries.append(str(seg.get("summary_gt", "") or ""))

                plan_path = _find_plan(plans_root, subject, video_id, str(seg.get("segment_id", "")))
                if plan_path is None:
                    issues.append(f"{subject}/{video_dir}:missing_plan:{stage}")
                    segs = []
                    break
                plan = _read_json(plan_path)
                plan_texts.append(serialize_plan(plan, id2kc=id2kc, id2tp=id2tp, cfg=plan_cfg))

            if not segs:
                continue

            gks = _build_gks_text(plan_texts)
            inp = (
                "[Macro Fusion]\n"
                + gks
                + "\n[Segment Summaries]\n"
                + "\n\n".join([f"Seg{i+1}: {seg_summaries[i]}" for i in range(4)])
                + "\n"
            )

            edu_out = str(macro.get("summary_edu_gt", "") or "")
            overall_out = str(macro.get("overall_summary_gt", "") or "")

            edu_rows.append(
                {
                    "messages": [{"role": "user", "content": inp}, {"role": "assistant", "content": edu_out}],
                    "meta": {"subject": subject, "video_id": video_id, "video_dir": video_dir, "task": "summary_edu"},
                }
            )
            overall_rows.append(
                {
                    "messages": [{"role": "user", "content": inp}, {"role": "assistant", "content": overall_out}],
                    "meta": {"subject": subject, "video_id": video_id, "video_dir": video_dir, "task": "overall_summary"},
                }
            )

    _write_jsonl(out_edu_jsonl, edu_rows)
    _write_jsonl(out_overall_jsonl, overall_rows)
    return (len(edu_rows), len(overall_rows)), issues


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build KCVR macro fusion SFT dataset (teacher forcing).")
    p.add_argument("--std-micro-root", type=Path, default=Path("data/annotations/standard_labels/micro"))
    p.add_argument("--std-macro-root", type=Path, default=Path("data/annotations/standard_labels/macro"))
    p.add_argument("--plans-root", type=Path, default=Path("cache/plans/micro_plans"))
    p.add_argument("--kg-raw-csv-root", type=Path, default=Path("knowledge_graph/raw_csv"))
    p.add_argument("--out-edu-jsonl", type=Path, default=Path("trainsets/macro_sft_edu_v1.jsonl"))
    p.add_argument("--out-overall-jsonl", type=Path, default=Path("trainsets/macro_sft_overall_v1.jsonl"))
    p.add_argument("--subjects", type=str, nargs="*", default=None)
    p.add_argument("--max-tp-anchors", type=int, default=2)
    p.add_argument("--max-kc-concepts", type=int, default=12)
    p.add_argument("--max-deps", type=int, default=5)
    p.add_argument("--report", type=Path, default=Path("experiments/v7.4_run1/macro_sft_build_issues.txt"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    subs = args.subjects or subject_order()
    cfg = PlanSerializeConfig(
        max_tp_anchors=args.max_tp_anchors,
        max_kc_concepts=args.max_kc_concepts,
        max_deps=args.max_deps,
    )
    (n_edu, n_overall), issues = build_macro_sft_teacher_forcing(
        std_micro_root=args.std_micro_root,
        std_macro_root=args.std_macro_root,
        plans_root=args.plans_root,
        kg_raw_csv_root=args.kg_raw_csv_root,
        out_edu_jsonl=args.out_edu_jsonl,
        out_overall_jsonl=args.out_overall_jsonl,
        subjects=subs,
        plan_cfg=cfg,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(issues), encoding="utf-8")
    print(
        f"macro_edu_samples={n_edu} macro_overall_samples={n_overall} issues={len(issues)} "
        f"out_edu={args.out_edu_jsonl} out_overall={args.out_overall_jsonl} report={args.report}"
    )


if __name__ == "__main__":
    main()




