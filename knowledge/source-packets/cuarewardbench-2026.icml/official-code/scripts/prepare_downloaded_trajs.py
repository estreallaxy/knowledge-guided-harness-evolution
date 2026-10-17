#!/usr/bin/env python3
"""Normalize downloaded trajectory archives to the CUARewardBench data layout.

The raw public archives may contain extra trajectories or multiple trials for a
single OSWorld task. This script treats ``data/manifest.jsonl`` as the source of
truth: for every expected trajectory, it searches the extracted raw directory for
candidate folders and copies only the candidate whose files match the manifest
(size + sha256 by default).

If no exact candidate is found, the script reports the mismatch and exits
non-zero instead of guessing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

CHUNK = 1024 * 1024
Key = Tuple[str, str, str]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def load_manifest(path: Path) -> Dict[Key, dict]:
    manifest: Dict[Key, dict] = {}
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            key = (entry["model_setting"], entry["task_type"], entry["task_id"])
            if key in manifest:
                raise ValueError(f"duplicate manifest key at line {line_no}: {key}")
            manifest[key] = entry
    return manifest


def load_expected_keys(annotation_file: Optional[Path], manifest: Dict[Key, dict]) -> List[Key]:
    if annotation_file is None:
        return list(manifest.keys())
    annotations = json.loads(annotation_file.read_text(encoding="utf-8"))
    keys: List[Key] = []
    seen = set()
    for i, item in enumerate(annotations):
        key = (item["model_setting"], item["task_type"], item["task_id"])
        if key in seen:
            continue
        seen.add(key)
        if key not in manifest:
            raise ValueError(f"annotation #{i} missing from manifest: {key}")
        keys.append(key)
    return keys


def is_hidden_path(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def has_trajectory_payload(path: Path) -> bool:
    has_png = False
    has_jsonl = False
    try:
        for child in path.iterdir():
            if child.name.startswith(".") or not child.is_file():
                continue
            if child.name.startswith("step_") and child.suffix.lower() == ".png":
                has_png = True
            elif child.name.startswith("traj") and child.suffix.lower() == ".jsonl":
                has_jsonl = True
            if has_png and has_jsonl:
                return True
    except OSError:
        return False
    return False


def iter_candidate_dirs(raw_root: Path) -> Iterable[Path]:
    for root, dirs, _files in raw_root.walk() if hasattr(raw_root, "walk") else _walk_compat(raw_root):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__MACOSX"]
        path = Path(root)
        if is_hidden_path(path.relative_to(raw_root)):
            continue
        if has_trajectory_payload(path):
            yield path


def _walk_compat(raw_root: Path):
    import os

    for root, dirs, files in os.walk(raw_root):
        yield root, dirs, files


def build_candidate_index(raw_root: Path, expected_keys: Sequence[Key]) -> Dict[Key, List[Path]]:
    model_settings = {k[0] for k in expected_keys}
    task_types = {k[1] for k in expected_keys}
    task_ids = {k[2] for k in expected_keys}
    by_task_id: Dict[str, List[Path]] = defaultdict(list)

    for candidate in iter_candidate_dirs(raw_root):
        parts = set(candidate.parts)
        matched_task_ids = parts & task_ids
        if not matched_task_ids:
            continue
        for task_id in matched_task_ids:
            by_task_id[task_id].append(candidate)

    index: Dict[Key, List[Path]] = {}
    for key in expected_keys:
        model_setting, task_type, task_id = key
        candidates = []
        for c in by_task_id.get(task_id, []):
            parts = set(c.parts)
            if task_type not in parts:
                continue
            # The downloader extracts each archive into raw_extracted/{model_setting}/.
            # If a user supplies a different raw tree, fall back to task_type/task_id match.
            if model_setting in parts or not (parts & model_settings):
                candidates.append(c)
            else:
                # Keep plausible candidates for opencua-style archive folder names;
                # manifest matching below will decide, not this heuristic.
                candidates.append(c)
        index[key] = sorted(set(candidates), key=lambda p: p.as_posix())
    return index


def normalized_jsonl_bytes(path: Path) -> bytes:
    lines = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                lines.append(json.dumps(json.loads(line), ensure_ascii=False))
    return ("\n".join(lines) + "\n").encode("utf-8")


def resolve_manifest_file(
    candidate: Path,
    rec: dict,
    kind: str,
    check_checksum: bool,
) -> Tuple[Optional[Path], str]:
    """Find the source file in a raw candidate for one manifest record.

    The canonical tree contains both ``traj.jsonl`` and ``traj_tran.jsonl`` for
    some trajectories, while the public archive may contain only ``traj.jsonl``
    with identical content. For trajectory jsonl files, allow a same-size and
    same-sha jsonl source to be copied under the manifest target name.
    Screenshot names remain strict.
    """
    exact = candidate / rec["name"]
    candidates = [exact]
    if kind == "traj_files":
        candidates.extend(
            p
            for p in sorted(candidate.glob("*.jsonl"), key=lambda x: x.name)
            if not p.name.startswith(".") and p != exact
        )

    seen = set()
    for fp in candidates:
        if fp in seen:
            continue
        seen.add(fp)
        if not fp.is_file():
            continue
        actual_size = fp.stat().st_size
        if actual_size != rec["size"]:
            continue
        if check_checksum:
            actual_sha = sha256_file(fp)
            if actual_sha != rec["sha256"]:
                continue
        return fp, "exact" if fp.name == rec["name"] else f"alias {fp.name} -> {rec['name']}"

    if kind == "traj_files" and rec["name"] == "traj_tran.jsonl":
        raw_traj = candidate / "traj.jsonl"
        if raw_traj.is_file():
            generated = normalized_jsonl_bytes(raw_traj)
            if len(generated) == rec["size"]:
                if not check_checksum or hashlib.sha256(generated).hexdigest() == rec["sha256"]:
                    return raw_traj, "generate traj.jsonl -> traj_tran.jsonl"

    if not exact.is_file():
        return None, f"missing {rec['name']}"
    actual_size = exact.stat().st_size
    if actual_size != rec["size"]:
        return None, f"size mismatch {rec['name']}: {actual_size} != {rec['size']}"
    if check_checksum:
        actual_sha = sha256_file(exact)
        return None, f"sha256 mismatch {rec['name']}: {actual_sha[:12]} != {rec['sha256'][:12]}"
    return None, f"unmatched {rec['name']}"


def candidate_matches_manifest(candidate: Path, entry: dict, check_checksum: bool) -> Tuple[bool, str]:
    alias_count = 0
    for kind in ("screenshots", "traj_files"):
        for rec in entry.get(kind, []):
            _fp, reason = resolve_manifest_file(candidate, rec, kind, check_checksum)
            if _fp is None:
                return False, reason
            if reason.startswith("alias ") or reason.startswith("generate "):
                alias_count += 1
    return True, "exact" if alias_count == 0 else f"exact with {alias_count} jsonl alias(es)"


def copy_manifest_files(candidate: Path, entry: dict, output_root: Path, check_checksum: bool) -> None:
    dest = output_root / entry["rel_dir"]
    dest.mkdir(parents=True, exist_ok=True)
    for kind in ("screenshots", "traj_files"):
        for rec in entry.get(kind, []):
            src, reason = resolve_manifest_file(candidate, rec, kind, check_checksum)
            if src is None:
                raise FileNotFoundError(f"{candidate}: {reason}")
            target = dest / rec["name"]
            if reason.startswith("generate "):
                target.write_bytes(normalized_jsonl_bytes(src))
            else:
                shutil.copy2(src, target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw_root", default=str(DEFAULT_WORKSPACE / "raw_extracted"))
    parser.add_argument("--output_root", default=str(DEFAULT_WORKSPACE / "prepared" / "osworld_verified"))
    parser.add_argument("--manifest", default="data/manifest.jsonl")
    parser.add_argument("--annotation_file", default="data/annotations/cuarewardbench-v0.4.json")
    parser.add_argument("--no-checksum", action="store_true", help="Match by file name and size only.")
    parser.add_argument("--dry-run", action="store_true", help="Only report matches; do not copy files.")
    parser.add_argument("--clean", action="store_true", help="Remove output_root before copying.")
    parser.add_argument("--max-errors", type=int, default=50)
    args = parser.parse_args()

    raw_root = Path(args.raw_root)
    output_root = Path(args.output_root)
    manifest_path = Path(args.manifest)
    annotation_file = Path(args.annotation_file) if args.annotation_file else None

    if not raw_root.is_dir():
        print(f"[ERROR] raw_root not found: {raw_root}", file=sys.stderr)
        return 2
    if not manifest_path.is_file():
        print(f"[ERROR] manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = load_manifest(manifest_path)
    expected_keys = load_expected_keys(annotation_file, manifest)
    print(f"[INFO] expected trajectories: {len(expected_keys)}")
    print(f"[INFO] scanning raw candidates under: {raw_root}")
    index = build_candidate_index(raw_root, expected_keys)

    selected: Dict[Key, Path] = {}
    missing: List[str] = []
    ambiguous: List[str] = []
    total_candidates = 0
    multi_candidate = 0
    check_checksum = not args.no_checksum

    for key in expected_keys:
        entry = manifest[key]
        candidates = index.get(key, [])
        total_candidates += len(candidates)
        if len(candidates) > 1:
            multi_candidate += 1

        exact: List[Path] = []
        mismatch_reasons: List[str] = []
        for c in candidates:
            ok, reason = candidate_matches_manifest(c, entry, check_checksum)
            if ok:
                exact.append(c)
            else:
                mismatch_reasons.append(f"{c}: {reason}")

        if len(exact) == 1:
            selected[key] = exact[0]
        elif len(exact) > 1:
            chosen = sorted(exact, key=lambda p: p.as_posix())[0]
            selected[key] = chosen
            ambiguous.append(f"{key}: {len(exact)} exact candidates, chose {chosen}")
        else:
            sample = "; ".join(mismatch_reasons[:3]) if mismatch_reasons else "no candidate directory"
            missing.append(f"{key}: {sample}")

    print(
        f"[INFO] candidate stats: total={total_candidates}, "
        f"keys_with_multiple_candidates={multi_candidate}"
    )
    print(f"[INFO] exact matches: {len(selected)}/{len(expected_keys)}")

    if ambiguous:
        print(f"[WARN] {len(ambiguous)} keys had multiple exact candidates:", file=sys.stderr)
        for item in ambiguous[: args.max_errors]:
            print(f"  - {item}", file=sys.stderr)
        if len(ambiguous) > args.max_errors:
            print(f"  ... ({len(ambiguous) - args.max_errors} more)", file=sys.stderr)

    if missing:
        print(f"[FAIL] {len(missing)} trajectories could not be matched exactly:", file=sys.stderr)
        for item in missing[: args.max_errors]:
            print(f"  - {item}", file=sys.stderr)
        if len(missing) > args.max_errors:
            print(f"  ... ({len(missing) - args.max_errors} more)", file=sys.stderr)
        print("[FAIL] stop here instead of guessing trial selection.", file=sys.stderr)
        return 1

    if args.dry_run:
        print("[OK] dry-run matched all trajectories; no files copied.")
        return 0

    if args.clean and output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    for i, key in enumerate(expected_keys, 1):
        copy_manifest_files(selected[key], manifest[key], output_root, check_checksum)
        if i % 50 == 0:
            print(f"[INFO] copied {i}/{len(expected_keys)}", flush=True)

    print(f"[OK] prepared normalized trajectories at: {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
