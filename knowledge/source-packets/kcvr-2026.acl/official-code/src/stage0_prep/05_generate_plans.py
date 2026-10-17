from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.stage0_prep.sg_planner_core import (  # noqa: E402
    GraphStore,
    PlannerConfig,
    TextSimilarity,
    plan_one_segment,
)
from src.utils.video_utils import subject_order  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _iter_micro_jsons(std_micro_root: Path, subject: str) -> List[Path]:
    subj_root = std_micro_root / subject
    if not subj_root.exists():
        return []
    return sorted([p for p in subj_root.rglob("*.json") if p.is_file()])


def _plan_id(video_id: str, segment_id: str) -> str:
    # Use stable, unique key across dataset
    return f"{video_id}__{segment_id}"


def generate_plans_for_subject(
    subject: str,
    std_micro_root: Path,
    kg_raw_csv_root: Path,
    out_dir: Path,
    cfg: PlannerConfig,
    embed_model: Optional[str],
    device: str,
) -> Tuple[int, List[str]]:
    """Generate plans for one subject.

    Args:
        subject: Canonical subject name (e.g., "math").
        std_micro_root: data/annotations/standard_labels/micro
        kg_raw_csv_root: knowledge_graph/raw_csv
        out_dir: cache/plans/micro_plans
        cfg: Planner config.
        embed_model: Optional embedding model path/name.
        device: "cpu" or "cuda".

    Returns:
        (count, issues)
    """
    issues: List[str] = []
    micro_files = _iter_micro_jsons(std_micro_root, subject)
    if not micro_files:
        issues.append(f"{subject}:no_micro_files")
        return 0, issues

    graph = GraphStore.load_from_raw_csv(kg_raw_csv_root, subject=subject)
    if not graph.kc_nodes:
        issues.append(f"{subject}:no_kc_nodes_loaded")
        return 0, issues

    similarity = TextSimilarity(model_name_or_path=embed_model, device=device)
    # Prepare corpus once per subject for stable & fast sim(transcript, kc_text)
    kc_ids = list(graph.kc_nodes.keys())
    kc_texts = [f"{graph.kc_nodes[k].name}。{graph.kc_nodes[k].definition}" for k in kc_ids]
    similarity.prepare_corpus(kc_ids, kc_texts)
    ok = 0
    for jf in micro_files:
        try:
            seg = _read_json(jf)
        except Exception as e:
            issues.append(f"{subject}:{jf}:json_load_error:{e}")
            continue

        video_id = str(seg.get("video_id", "") or "")
        segment_id = str(seg.get("segment_id", "") or "")
        stage = str(seg.get("stage", "") or "")
        text_input = str(seg.get("text_input", "") or "")
        objectives = seg.get("objectives_gt", []) or []
        knowledge_points = seg.get("knowledge_points", []) or []

        if not video_id or not segment_id:
            issues.append(f"{subject}:{jf}:missing_video_or_segment_id")
            continue

        plan = plan_one_segment(
            graph=graph,
            transcript=text_input,
            objectives=list(objectives) if isinstance(objectives, list) else [str(objectives)],
            knowledge_points=list(knowledge_points) if isinstance(knowledge_points, list) else [],
            config=cfg,
            similarity=similarity,
        )

        # Attach human-readable names to stabilize downstream plan-text serialization & evaluation.
        kc_ids = plan.get("kc_nodes", []) or []
        tp_ids = plan.get("tp_nodes", []) or []
        kc_names = [graph.kc_nodes[k].name for k in kc_ids if k in graph.kc_nodes]
        tp_names = [graph.tp_nodes[t].name for t in tp_ids if t in graph.tp_nodes]

        # Schema compatibility: provide both "nodes_* / edges_* / pi" and the internal keys.
        edges = plan.get("edges", {}) or {}
        edges_based_on = edges.get("BASED_ON", [])
        edges_has_concept = edges.get("HAS_CONCEPT", [])
        edges_next_tp = edges.get("NEXT_TP", [])

        plan_out = {
            "plan_id": _plan_id(video_id, segment_id),
            "subject": subject,
            "video_id": video_id,
            "segment_id": segment_id,
            "stage": stage,
            "source_label_path": jf.as_posix(),
            **plan,
            # recommended schema aliases
            "nodes_kc": plan.get("kc_nodes", []),
            "nodes_tp": plan.get("tp_nodes", []),
            "nodes_kc_name": kc_names,
            "nodes_tp_name": tp_names,
            "edges_based_on": edges_based_on,
            "edges_has_concept": edges_has_concept,
            "edges_next": edges_next_tp,
            "pi": plan.get("pi_kc", []),
        }

        out_path = out_dir / subject / video_id / f"{_plan_id(video_id, segment_id)}.json"
        _write_json(out_path, plan_out)
        ok += 1

    return ok, issues


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SG-Planner batch plan generation for KCVR (Stage 0).")
    p.add_argument("--subjects", type=str, nargs="*", default=None, help="Subjects (default: all 10 subjects).")
    p.add_argument(
        "--std-micro-root",
        type=Path,
        default=Path("data/annotations/standard_labels/micro"),
        help="Root of standardized micro labels.",
    )
    p.add_argument(
        "--kg-raw-csv-root",
        type=Path,
        default=Path("knowledge_graph/raw_csv"),
        help="Root of aggregated KG csvs (nodes_kc/nodes_tp/relations).",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("cache/plans/micro_plans"),
        help="Output dir for plans.",
    )
    p.add_argument("--seed-top-k", type=int, default=20)
    p.add_argument("--final-top-b", type=int, default=10)
    p.add_argument("--alpha-match", type=float, default=0.6)
    p.add_argument("--sim-threshold", type=float, default=0.3)
    p.add_argument("--embed-model", type=str, default=None, help="Optional SentenceTransformer model path/name.")
    p.add_argument("--device", type=str, default="cpu", help="cpu/cuda (only affects embedding backend if used).")
    p.add_argument(
        "--report",
        type=Path,
        default=Path("experiments/v7.4_run1/sg_planner_issues.txt"),
        help="Issues report output.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    subs = args.subjects or subject_order()
    # If user already downloaded bge-m3 locally, prefer it by default when not specified.
    if args.embed_model is None:
        local_bge = Path("models/bge-m3")
        if local_bge.exists():
            args.embed_model = local_bge.as_posix()
            if args.device == "cpu":
                # Safe default: let user override, but prefer cuda if available in their env.
                args.device = "cuda"
    cfg = PlannerConfig(
        seed_top_k=args.seed_top_k,
        final_top_b=args.final_top_b,
        alpha_match=args.alpha_match,
        sim_threshold=args.sim_threshold,
        max_swap_iters=max(50, args.final_top_b * args.final_top_b),
    )

    total_ok = 0
    all_issues: List[str] = []
    for subj in subs:
        ok, issues = generate_plans_for_subject(
            subject=subj,
            std_micro_root=args.std_micro_root,
            kg_raw_csv_root=args.kg_raw_csv_root,
            out_dir=args.out_dir,
            cfg=cfg,
            embed_model=args.embed_model,
            device=args.device,
        )
        total_ok += ok
        all_issues.extend(issues)
        logger.info("SG-Planner done subject=%s plans=%d issues=%d", subj, ok, len(issues))

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(all_issues), encoding="utf-8")
    print(f"plans={total_ok} issues={len(all_issues)} report={args.report} out={args.out_dir}")


if __name__ == "__main__":
    main()



