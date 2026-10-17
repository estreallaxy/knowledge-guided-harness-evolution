from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.stage0_prep.sg_planner_core import _normalize_concept_phrase  # noqa: E402


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class PlanStats:
    """Aggregated statistics of plan outputs."""

    num_plans: int
    kc_mean: float
    kc_p50: float
    tp_mean: float
    tp_p50: float
    kp_recall_mean: float
    kp_recall_p50: float
    kp_recall_ge_80: float
    kp_recall_ge_50: float
    empty_kp_ratio: float


def _safe_p50(xs: Sequence[float]) -> float:
    if not xs:
        return 0.0
    return float(statistics.median(xs))


def _safe_mean(xs: Sequence[float]) -> float:
    if not xs:
        return 0.0
    return float(statistics.mean(xs))


def eval_plans(plans_root: Path, subject: Optional[str] = None) -> Tuple[PlanStats, List[Dict[str, Any]]]:
    """Evaluate generated plans and return summary stats plus worst cases.

    Args:
        plans_root: Root directory containing plan json files.
        subject: Optional subject filter.

    Returns:
        (stats, worst_cases)
    """
    files = sorted(plans_root.rglob("*.json"))
    if subject:
        files = [p for p in files if f"/{subject}/" in p.as_posix()]

    kc_counts: List[float] = []
    tp_counts: List[float] = []
    kp_recalls: List[float] = []
    cases: List[Dict[str, Any]] = []
    empty_kp = 0

    for p in files:
        data = _read_json(p)
        kc = data.get("nodes_kc") or data.get("kc_nodes") or []
        tp = data.get("nodes_tp") or data.get("tp_nodes") or []
        debug = data.get("debug") or {}

        # Prefer recomputing kp_recall from source label + nodes_kc_name to avoid systemic underestimation.
        source = data.get("source_label_path")
        nodes_kc_name = data.get("nodes_kc_name") or []
        kp_total = 0
        kp_hit = 0
        kp_recall_val: Optional[float] = None
        if source and Path(str(source)).exists() and nodes_kc_name:
            seg = _read_json(Path(str(source)))
            kp_list = seg.get("knowledge_points") or []
            kp_core: List[str] = []
            for x in kp_list:
                if isinstance(x, dict) and x.get("name"):
                    core = _normalize_concept_phrase(str(x["name"]))
                    if core:
                        kp_core.append(core)
            kc_core = [_normalize_concept_phrase(str(n)) for n in nodes_kc_name]
            kc_core = [x for x in kc_core if x]
            kp_total = len(kp_core)
            for core in kp_core:
                hit = False
                for kn in kc_core:
                    if core == kn or core in kn or kn in core:
                        hit = True
                        break
                if not hit:
                    try:
                        from rapidfuzz import fuzz  # type: ignore

                        if any(fuzz.ratio(core, kn) >= 85 for kn in kc_core):
                            hit = True
                    except Exception:
                        pass
                if hit:
                    kp_hit += 1
            kp_recall_val = (float(kp_hit) / float(kp_total)) if kp_total > 0 else None
        else:
            kp_total = int(debug.get("kp_total") or 0)
            kp_hit = int(debug.get("kp_hit") or 0)
            kp_recall_val = debug.get("kp_recall", None)

        if kp_total == 0:
            empty_kp += 1
        if kp_recall_val is not None:
            kp_recalls.append(float(kp_recall_val))
        kc_counts.append(float(len(kc)))
        tp_counts.append(float(len(tp)))
        cases.append(
            {
                "path": p.as_posix(),
                "plan_id": data.get("plan_id", ""),
                "subject": data.get("subject", ""),
                "video_id": data.get("video_id", ""),
                "segment_id": data.get("segment_id", ""),
                "stage": data.get("stage", ""),
                "kp_total": kp_total,
                "kp_hit": kp_hit,
                "kp_recall": float(kp_recall_val) if kp_recall_val is not None else None,
                "kc_n": len(kc),
                "tp_n": len(tp),
                "top_modules": debug.get("top_modules", []),
                "sim_backend": debug.get("sim_backend", ""),
            }
        )

    num = len(files)
    denom = max(1, len(kp_recalls))
    ge80 = sum(1 for x in kp_recalls if x >= 0.8) / float(denom)
    ge50 = sum(1 for x in kp_recalls if x >= 0.5) / float(denom)
    empty_ratio = float(empty_kp) / float(max(1, num))

    stats = PlanStats(
        num_plans=num,
        kc_mean=_safe_mean(kc_counts),
        kc_p50=_safe_p50(kc_counts),
        tp_mean=_safe_mean(tp_counts),
        tp_p50=_safe_p50(tp_counts),
        kp_recall_mean=_safe_mean(kp_recalls),
        kp_recall_p50=_safe_p50(kp_recalls),
        kp_recall_ge_80=float(ge80),
        kp_recall_ge_50=float(ge50),
        empty_kp_ratio=empty_ratio,
    )

    worst = sorted([c for c in cases if c["kp_recall"] is not None], key=lambda x: float(x["kp_recall"]))[:20]
    return stats, worst


def _write_markdown(path: Path, stats: PlanStats, worst_cases: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# SG-Planner Plan Evaluation\n")
    lines.append("## Summary\n")
    lines.append(f"- num_plans: **{stats.num_plans}**")
    lines.append(f"- kc_mean / kc_p50: **{stats.kc_mean:.2f} / {stats.kc_p50:.2f}**")
    lines.append(f"- tp_mean / tp_p50: **{stats.tp_mean:.2f} / {stats.tp_p50:.2f}**")
    lines.append(f"- kp_recall_mean / kp_recall_p50: **{stats.kp_recall_mean:.3f} / {stats.kp_recall_p50:.3f}**")
    lines.append(f"- kp_recall>=0.8: **{stats.kp_recall_ge_80:.3f}**")
    lines.append(f"- kp_recall>=0.5: **{stats.kp_recall_ge_50:.3f}**\n")
    lines.append(f"- empty_kp_ratio (kp_total==0): **{stats.empty_kp_ratio:.3f}**\n")
    lines.append("## Worst 20 cases by kp_recall\n")
    lines.append("|kp_recall|kp_hit/kp_total|kc_n|tp_n|stage|sim_backend|video_id|segment_id|path|")
    lines.append("|---:|---:|---:|---:|---|---|---|---|---|")
    for c in worst_cases:
        lines.append(
            f"|{float(c['kp_recall']):.3f}|{c['kp_hit']}/{c['kp_total']}|{c['kc_n']}|{c['tp_n']}|{c['stage']}|{c.get('sim_backend','')}|{c['video_id']}|{c['segment_id']}|`{c['path']}`|"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate SG-Planner outputs (kp_recall / sizes).")
    p.add_argument("--plans-root", type=Path, default=Path("cache/plans/micro_plans"))
    p.add_argument("--subject", type=str, default=None)
    p.add_argument("--out-md", type=Path, default=Path("experiments/v7.4_run1/sg_planner_eval.md"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    stats, worst = eval_plans(args.plans_root, subject=args.subject)
    _write_markdown(args.out_md, stats, worst)
    print(f"wrote={args.out_md} num={stats.num_plans} kp_mean={stats.kp_recall_mean:.3f}")


if __name__ == "__main__":
    main()


