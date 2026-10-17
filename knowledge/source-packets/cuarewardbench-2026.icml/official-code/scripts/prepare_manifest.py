#!/usr/bin/env python3
"""Generate ``data/manifest.jsonl`` for CUARewardBench trajectories.

For every ``(model_setting, task_type, task_id)`` referenced by the annotation
file, scan the corresponding trajectory directory and record the file size and
sha256 of every screenshot and trajectory ``.jsonl`` file.

The resulting manifest enables ``scripts/verify_data.py`` to detect missing,
extra, or corrupted files after users download the trajectory bundle from the
release artifacts. macOS dotted-resource files (``._foo``) and hidden files are
ignored.

Usage
-----
    python3 scripts/prepare_manifest.py \
        --annotation_file data/annotations/cuarewardbench-v0.4.json \
        --trajectory_root data/trajectories/osworld_verified \
        --output data/manifest.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CHUNK = 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def list_trajectory_files(traj_dir: Path) -> Tuple[List[Path], List[Path]]:
    """Return (screenshots, traj_jsonls), each sorted by filename.

    Skips macOS ``._*`` files and any other dotfiles.
    """
    screenshots: List[Path] = []
    traj_files: List[Path] = []
    if not traj_dir.is_dir():
        return screenshots, traj_files
    for entry in sorted(traj_dir.iterdir(), key=lambda p: p.name):
        if entry.name.startswith("."):
            continue
        if not entry.is_file():
            continue
        if entry.suffix.lower() == ".png" and entry.name.startswith("step_"):
            screenshots.append(entry)
        elif entry.suffix.lower() == ".jsonl" and entry.name.startswith("traj"):
            traj_files.append(entry)
    return screenshots, traj_files


def build_entry(
    model_setting: str,
    task_type: str,
    task_id: str,
    trajectory_root: Path,
) -> Tuple[Optional[dict], Optional[str]]:
    traj_dir = trajectory_root / model_setting / task_type / task_id
    if not traj_dir.is_dir():
        return None, f"missing dir: {traj_dir}"

    screenshots, traj_files = list_trajectory_files(traj_dir)
    if not screenshots:
        return None, f"no screenshots in: {traj_dir}"
    if not traj_files:
        return None, f"no traj jsonl in: {traj_dir}"

    rel_dir = Path(model_setting) / task_type / task_id

    def _file_record(p: Path) -> dict:
        return {
            "name": p.name,
            "size": p.stat().st_size,
            "sha256": sha256_file(p),
        }

    entry = {
        "model_setting": model_setting,
        "task_type": task_type,
        "task_id": task_id,
        "rel_dir": rel_dir.as_posix(),
        "num_screenshots": len(screenshots),
        "screenshots": [_file_record(p) for p in screenshots],
        "traj_files": [_file_record(p) for p in traj_files],
    }
    return entry, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--annotation_file",
        default="data/annotations/cuarewardbench-v0.4.json",
        help="Path to CUARewardBench annotation JSON.",
    )
    parser.add_argument(
        "--trajectory_root",
        default="data/trajectories/osworld_verified",
        help="Root directory containing {model_setting}/{task_type}/{task_id}/ folders.",
    )
    parser.add_argument(
        "--output",
        default="data/manifest.jsonl",
        help="Output manifest JSONL path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any annotation entry has missing trajectory data.",
    )
    args = parser.parse_args()

    ann_path = Path(args.annotation_file)
    traj_root = Path(args.trajectory_root)
    out_path = Path(args.output)

    if not ann_path.is_file():
        print(f"[ERROR] annotation file not found: {ann_path}", file=sys.stderr)
        return 2
    if not traj_root.is_dir():
        print(f"[ERROR] trajectory root not found: {traj_root}", file=sys.stderr)
        return 2

    annotations = json.loads(ann_path.read_text(encoding="utf-8"))
    if not isinstance(annotations, list):
        print("[ERROR] annotation file must be a JSON list", file=sys.stderr)
        return 2

    seen: Dict[Tuple[str, str, str], dict] = {}
    missing: List[str] = []

    for i, item in enumerate(annotations):
        try:
            ms = item["model_setting"]
            tt = item["task_type"]
            tid = item["task_id"]
        except KeyError as e:
            print(f"[ERROR] annotation #{i} missing key {e}", file=sys.stderr)
            return 2

        key = (ms, tt, tid)
        if key in seen:
            continue
        entry, err = build_entry(ms, tt, tid, traj_root)
        if err is not None:
            missing.append(err)
            continue
        seen[key] = entry
        if (len(seen) % 50) == 0:
            print(f"[INFO] processed {len(seen)} unique trajectories", flush=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for entry in seen.values():
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    total_screens = sum(e["num_screenshots"] for e in seen.values())
    total_bytes = sum(
        sum(s["size"] for s in e["screenshots"]) + sum(t["size"] for t in e["traj_files"])
        for e in seen.values()
    )
    print(
        f"[DONE] manifest: {out_path}  "
        f"trajectories={len(seen)} screenshots={total_screens} "
        f"size={total_bytes / 1e9:.2f} GB"
    )
    if missing:
        print(f"[WARN] {len(missing)} trajectories missing or empty:", file=sys.stderr)
        for m in missing[:20]:
            print(f"  - {m}", file=sys.stderr)
        if len(missing) > 20:
            print(f"  ... ({len(missing) - 20} more)", file=sys.stderr)
        if args.strict:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
