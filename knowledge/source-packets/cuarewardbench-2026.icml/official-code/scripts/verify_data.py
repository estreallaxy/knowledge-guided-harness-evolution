#!/usr/bin/env python3
"""Verify ``data/trajectories/`` against ``data/manifest.jsonl``.

Checks, for every manifest entry:
  * the trajectory directory exists;
  * every recorded file exists, with matching size;
  * (optionally) every recorded file's sha256 matches.

By default sha256 is checked. Pass ``--no-checksum`` to do a fast size-only
sanity check (e.g. right after running ``download_data.sh``).

Exit code is 0 on success, 1 on any verification failure, 2 on usage / IO
errors.

Usage
-----
    python3 scripts/verify_data.py
    python3 scripts/verify_data.py --no-checksum   # fast pre-check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import List

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


def verify_one(entry: dict, traj_root: Path, check_sum: bool) -> List[str]:
    errors: List[str] = []
    rel_dir = entry["rel_dir"]
    base = traj_root / rel_dir
    if not base.is_dir():
        return [f"missing directory: {rel_dir}"]

    for kind in ("screenshots", "traj_files"):
        for rec in entry.get(kind, []):
            fp = base / rec["name"]
            if not fp.is_file():
                errors.append(f"missing file: {rel_dir}/{rec['name']}")
                continue
            actual_size = fp.stat().st_size
            if actual_size != rec["size"]:
                errors.append(
                    f"size mismatch: {rel_dir}/{rec['name']} "
                    f"expect={rec['size']} actual={actual_size}"
                )
                continue
            if check_sum:
                actual = sha256_file(fp)
                if actual != rec["sha256"]:
                    errors.append(
                        f"sha256 mismatch: {rel_dir}/{rec['name']} "
                        f"expect={rec['sha256'][:12]}.. actual={actual[:12]}.."
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="data/manifest.jsonl",
        help="Path to manifest.jsonl",
    )
    parser.add_argument(
        "--trajectory_root",
        default="data/trajectories/osworld_verified",
        help="Root directory containing {model_setting}/{task_type}/{task_id}/ folders.",
    )
    parser.add_argument(
        "--no-checksum",
        action="store_true",
        help="Only verify file existence and size; skip sha256.",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=50,
        help="Max errors to print before truncating output (default: 50).",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    traj_root = Path(args.trajectory_root)
    if not manifest_path.is_file():
        print(f"[ERROR] manifest not found: {manifest_path}", file=sys.stderr)
        return 2
    if not traj_root.is_dir():
        print(f"[ERROR] trajectory root not found: {traj_root}", file=sys.stderr)
        return 2

    entries = []
    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))

    check_sum = not args.no_checksum
    mode = "sha256" if check_sum else "size-only"
    print(f"[INFO] verifying {len(entries)} trajectories ({mode}) ...")

    all_errors: List[str] = []
    ok_count = 0
    for i, entry in enumerate(entries):
        errs = verify_one(entry, traj_root, check_sum)
        if errs:
            all_errors.extend(errs)
        else:
            ok_count += 1
        if (i + 1) % 50 == 0:
            print(f"[INFO] processed {i + 1}/{len(entries)} (ok so far={ok_count})", flush=True)

    if all_errors:
        print(
            f"[FAIL] {ok_count}/{len(entries)} trajectories ok, "
            f"{len(all_errors)} file-level errors:",
            file=sys.stderr,
        )
        for e in all_errors[: args.max_errors]:
            print(f"  - {e}", file=sys.stderr)
        if len(all_errors) > args.max_errors:
            print(f"  ... ({len(all_errors) - args.max_errors} more)", file=sys.stderr)
        return 1

    print(f"[OK] all {len(entries)} trajectories verified ({mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
