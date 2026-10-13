"""Prepare the public, revision-pinned MathArena AIME datasets."""

import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


_SOURCES = {
    2025: ("c94da77eb22bbd6439e62a323bec18493a421302", "9f9066ff48ad2e31f9bf1b1ac6d5e80693195f987985f2859f89dd25ffa51c2d"),
    2026: ("d2de22f3c656b4f56cf8981212186377d1e23bc3", "d91db799651b4cc1f0734f52792a695c9cc60dac342524b3d8e5b2ff31c3e957"),
}
_LICENSE = "cc-by-nc-sa-4.0"


def _read_parquet(path: Path) -> list[dict]:
    try:
        import pyarrow.parquet as parquet
    except ImportError:
        raise ValueError("Dataset preparation requires: pip install 'llm-discussion[benchmarks]'") from None
    return parquet.read_table(path).to_pylist()


def prepare_aime(output: Path, *, year: int = 2025, limit: int | None = None) -> Path:
    """Write numeric tasks, original annotations, and source provenance.

    Both years contain 30 problems. The upstream split is named ``train`` but
    these are competition evaluation problems, not examples supplied to models.
    ``limit`` selects the first problems in source order, without using labels.
    """
    if type(year) is not int or year not in _SOURCES:
        raise ValueError("AIME year must be 2025 or 2026")
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("limit must be a positive integer or null")
    output = Path(output).resolve()
    revision, expected_hash = _SOURCES[year]
    repo = f"MathArena/aime_{year}"
    source_file = "data/train-00000-of-00001.parquet"
    url = f"https://huggingface.co/datasets/{repo}/resolve/{revision}/{source_file}"
    metadata = output / "source" / f"aime-{year}-{revision}.parquet"
    if not metadata.exists():
        with urlopen(url, timeout=60) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError("AIME metadata SHA-256 does not match the pinned source")
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_bytes(content)
    content_hash = hashlib.sha256(metadata.read_bytes()).hexdigest()
    if content_hash != expected_hash:
        raise ValueError("Cached AIME metadata SHA-256 does not match the pinned source")
    rows = _read_parquet(metadata)
    if len(rows) != 30:
        raise ValueError("Pinned AIME dataset must contain exactly 30 problems")
    selected = rows[:limit] if limit is not None else rows
    tasks = []
    for row in selected:
        index, question, answer = row.get("problem_idx"), row.get("problem"), row.get("answer")
        if (type(index) is not int or not isinstance(question, str) or not question.strip()
                or type(answer) is not int or not 0 <= answer <= 999):
            raise ValueError("Unexpected AIME source schema")
        tasks.append({
            "id": f"aime-{year}-{index}", "question": question,
            "reference": str(answer), "answer_type": "number", "options": [], "images": [],
            "category": ", ".join(row.get("problem_type") or [f"AIME {year}"]),
        })
    if len({row["id"] for row in tasks}) != len(tasks):
        raise ValueError("AIME source contains duplicate problem IDs")
    tasks_path = output / "tasks.jsonl"
    tasks_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in tasks), encoding="utf-8")
    provenance = {
        "dataset": f"AIME {year}", "source_repo": repo, "source_revision": revision,
        "source_url": url, "source_split": "train", "license": _LICENSE,
        "metadata_path": metadata.relative_to(output).as_posix(), "metadata_sha256": content_hash,
        "available_tasks": len(rows), "prepared_tasks": len(tasks),
        "selection": {"limit": limit, "order": "source order"}, "metric": "numeric_exact_match",
        "tasks_sha256": hashlib.sha256(tasks_path.read_bytes()).hexdigest(),
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    return tasks_path
