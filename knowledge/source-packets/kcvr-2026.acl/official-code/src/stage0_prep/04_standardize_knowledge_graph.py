from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.utils.csv_utils import read_csv_dicts, write_csv_dicts  # noqa: E402
from src.utils.video_utils import subject_order  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass(frozen=True)
class KcRow:
    """A normalized KnowledgeConcept row."""

    id: str
    name: str
    level: int
    definition: str
    subject: str
    first_appear_module: str
    label: str


@dataclass(frozen=True)
class TpRow:
    """A normalized TeachingPoint row."""

    id: str
    name: str
    level: int
    description: str
    subject: str
    label: str


@dataclass(frozen=True)
class RelRow:
    """A normalized relation row."""

    start_id: str
    end_id: str
    rel_type: str


def _strip(x: Optional[str]) -> str:
    return (x or "").strip()


def _to_int(x: str, default: int = 0) -> int:
    try:
        return int(float(x))
    except Exception:
        return default


def _infer_tp_module(tp_id: str) -> Optional[str]:
    """Infer module token from a TP id like 'tp_math_alg1_ch1_sec1'.

    Args:
        tp_id: TP node id.

    Returns:
        Module token if parsable, else None.
    """
    if not tp_id.startswith("tp_"):
        return None
    parts = tp_id.split("_")
    # Expected: tp_{subj_code}_{module}_...
    if len(parts) >= 3:
        mod = parts[2].strip()
        return mod or None
    return None


def _load_subject_paths(subjects_root: Path, subject: str) -> Tuple[Path, Path, Path]:
    subj_dir = subjects_root / subject
    if not subj_dir.exists():
        raise FileNotFoundError(f"Missing subject dir: {subj_dir}")
    # Most subjects follow: {prefix}_TeachingPoint_nodes.csv, {prefix}_KnowledgeConcept_nodes.csv, {prefix}_relations.csv
    kc_files = sorted(subj_dir.glob("*_KnowledgeConcept_nodes.csv"))
    tp_files = sorted(subj_dir.glob("*_TeachingPoint_nodes.csv"))
    rel_files = sorted(subj_dir.glob("*_relations.csv"))
    if not kc_files or not tp_files or not rel_files:
        raise FileNotFoundError(f"Missing csvs under: {subj_dir}")
    return kc_files[0], tp_files[0], rel_files[0]


def _build_kc_to_tp_modules(rel_rows: Iterable[RelRow]) -> Dict[str, List[str]]:
    kc_to_mods: Dict[str, List[str]] = defaultdict(list)
    for r in rel_rows:
        if r.rel_type != "HAS_CONCEPT":
            continue
        tp_mod = _infer_tp_module(r.start_id)
        if tp_mod:
            kc_to_mods[r.end_id].append(tp_mod)
    return kc_to_mods


def _normalize_kc_rows(
    subject: str,
    raw_rows: List[Dict[str, str]],
    kc_to_tp_modules: Dict[str, List[str]],
) -> Tuple[List[KcRow], List[str]]:
    issues: List[str] = []
    out: List[KcRow] = []
    seen: Set[str] = set()
    for i, row in enumerate(raw_rows):
        rid = _strip(row.get("id"))
        if not rid:
            issues.append(f"{subject}:kc:row{i}:missing_id")
            continue
        if rid in seen:
            issues.append(f"{subject}:kc:dup_id:{rid}")
            continue
        seen.add(rid)

        name = _strip(row.get("name"))
        definition = _strip(row.get("definition"))
        level = _to_int(_strip(row.get("level")), default=0)
        label = _strip(row.get(":LABEL")) or "KnowledgeConcept"

        fam = _strip(row.get("first_appear_module"))
        if not fam:
            mods = kc_to_tp_modules.get(rid, [])
            if mods:
                fam = Counter(mods).most_common(1)[0][0]
        if not fam:
            fam = "unknown"
            issues.append(f"{subject}:kc:{rid}:missing_first_appear_module->unknown")

        if not name:
            issues.append(f"{subject}:kc:{rid}:missing_name")
        if not definition:
            # Fill with name to keep embedding/indexing pipeline functional.
            definition = name
            issues.append(f"{subject}:kc:{rid}:missing_definition->filled_with_name")

        out.append(
            KcRow(
                id=rid,
                name=name,
                level=level,
                definition=definition,
                subject=subject,
                first_appear_module=fam,
                label=label,
            )
        )
    return out, issues


def _normalize_tp_rows(subject: str, raw_rows: List[Dict[str, str]]) -> Tuple[List[TpRow], List[str]]:
    issues: List[str] = []
    out: List[TpRow] = []
    seen: Set[str] = set()
    for i, row in enumerate(raw_rows):
        rid = _strip(row.get("id"))
        if not rid:
            issues.append(f"{subject}:tp:row{i}:missing_id")
            continue
        if rid in seen:
            issues.append(f"{subject}:tp:dup_id:{rid}")
            continue
        seen.add(rid)

        name = _strip(row.get("name"))
        desc = _strip(row.get("description"))
        level = _to_int(_strip(row.get("level")), default=0)
        label = _strip(row.get(":LABEL")) or "TeachingPoint"

        if not name:
            issues.append(f"{subject}:tp:{rid}:missing_name")
        if not desc:
            issues.append(f"{subject}:tp:{rid}:missing_description")

        out.append(TpRow(id=rid, name=name, level=level, description=desc, subject=subject, label=label))
    return out, issues


def _normalize_rel_rows(raw_rows: List[Dict[str, str]]) -> Tuple[List[RelRow], List[str]]:
    issues: List[str] = []
    out: List[RelRow] = []
    for i, row in enumerate(raw_rows):
        sid = _strip(row.get(":START_ID"))
        eid = _strip(row.get(":END_ID"))
        rtype = _strip(row.get(":TYPE"))
        if not sid or not eid or not rtype:
            issues.append(f"rel:row{i}:missing_fields")
            continue
        out.append(RelRow(start_id=sid, end_id=eid, rel_type=rtype))
    return out, issues


def _kc_to_dict(r: KcRow) -> Dict[str, str]:
    return {
        "id": r.id,
        "name": r.name,
        "level": str(r.level),
        "definition": r.definition,
        "subject": r.subject,
        "first_appear_module": r.first_appear_module,
        "subject_module": f"{r.subject}:{r.first_appear_module}",
        ":LABEL": r.label,
    }


def _tp_to_dict(r: TpRow) -> Dict[str, str]:
    return {
        "id": r.id,
        "name": r.name,
        "level": str(r.level),
        "description": r.description,
        "subject": r.subject,
        ":LABEL": r.label,
    }


def _rel_to_dict(r: RelRow) -> Dict[str, str]:
    return {":START_ID": r.start_id, ":END_ID": r.end_id, ":TYPE": r.rel_type}


def standardize_all(
    subjects_root: Path,
    out_root: Path,
    subjects: Sequence[str],
) -> Tuple[Dict[str, int], List[str]]:
    """Standardize 10-subject knowledge graphs into unified CSVs.

    This function exports:
    - Per-subject cleaned CSVs under out_root/processed/{subject}/
    - Aggregated CSVs under out_root/raw_csv/{nodes_tp.csv,nodes_kc.csv,relations.csv}

    Args:
        subjects_root: knowledge_graph/subjects
        out_root: knowledge_graph root
        subjects: subject list

    Returns:
        (stats, issues)
    """
    issues: List[str] = []
    all_tp: List[TpRow] = []
    all_kc: List[KcRow] = []
    all_rel: List[RelRow] = []

    processed_root = out_root / "processed"
    raw_csv_root = out_root / "raw_csv"

    for subject in subjects:
        kc_path, tp_path, rel_path = _load_subject_paths(subjects_root, subject)
        kc_raw = read_csv_dicts(kc_path)
        tp_raw = read_csv_dicts(tp_path)
        rel_raw = read_csv_dicts(rel_path)

        rel_rows, rel_issues = _normalize_rel_rows(rel_raw)
        issues.extend([f"{subject}:{x}" for x in rel_issues])
        kc_to_tp_modules = _build_kc_to_tp_modules(rel_rows)

        kc_rows, kc_issues = _normalize_kc_rows(subject, kc_raw, kc_to_tp_modules)
        tp_rows, tp_issues = _normalize_tp_rows(subject, tp_raw)
        issues.extend(kc_issues)
        issues.extend(tp_issues)

        all_kc.extend(kc_rows)
        all_tp.extend(tp_rows)
        all_rel.extend(rel_rows)

        subj_out = processed_root / subject
        write_csv_dicts(
            subj_out / "nodes_kc.csv",
            [_kc_to_dict(r) for r in kc_rows],
            fieldnames=["id", "name", "level", "definition", "subject", "first_appear_module", "subject_module", ":LABEL"],
        )
        write_csv_dicts(
            subj_out / "nodes_tp.csv",
            [_tp_to_dict(r) for r in tp_rows],
            fieldnames=["id", "name", "level", "description", "subject", ":LABEL"],
        )
        write_csv_dicts(
            subj_out / "relations.csv",
            [_rel_to_dict(r) for r in rel_rows],
            fieldnames=[":START_ID", ":END_ID", ":TYPE"],
        )

        logger.info(
            "KG subject=%s kc=%d tp=%d rel=%d",
            subject,
            len(kc_rows),
            len(tp_rows),
            len(rel_rows),
        )

    # Aggregated exports for downstream indexing/trie
    write_csv_dicts(
        raw_csv_root / "nodes_kc.csv",
        [_kc_to_dict(r) for r in all_kc],
        fieldnames=["id", "name", "level", "definition", "subject", "first_appear_module", "subject_module", ":LABEL"],
    )
    write_csv_dicts(
        raw_csv_root / "nodes_tp.csv",
        [_tp_to_dict(r) for r in all_tp],
        fieldnames=["id", "name", "level", "description", "subject", ":LABEL"],
    )
    write_csv_dicts(
        raw_csv_root / "relations.csv",
        [_rel_to_dict(r) for r in all_rel],
        fieldnames=[":START_ID", ":END_ID", ":TYPE"],
    )

    stats = {
        "subjects": len(subjects),
        "kc": len(all_kc),
        "tp": len(all_tp),
        "relations": len(all_rel),
        "issues": len(issues),
    }
    return stats, issues


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Standardize 10-subject knowledge graphs into unified CSVs.")
    p.add_argument("--kg-root", type=Path, default=Path("knowledge_graph"))
    p.add_argument("--subjects-root", type=Path, default=Path("knowledge_graph/subjects"))
    p.add_argument("--subjects", type=str, nargs="*", default=None)
    p.add_argument("--report", type=Path, default=Path("experiments/v7.4_run1/kg_standardize_issues.txt"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    subs = args.subjects or subject_order()
    stats, issues = standardize_all(args.subjects_root, args.kg_root, subs)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(issues), encoding="utf-8")
    print(f"stats={stats} report={args.report}")


if __name__ == "__main__":
    main()


