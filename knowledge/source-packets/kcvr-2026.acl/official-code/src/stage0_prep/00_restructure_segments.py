from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CATS = ["intro", "exposition", "interaction", "conclusion"]


def canonical_video_id(subject: str, video_dir_name: str) -> str:
    if video_dir_name.startswith(f"{subject}_"):
        return video_dir_name
    # fix double prefix case like subject_subject_xxx
    if video_dir_name.startswith(f"{subject}_{subject}_"):
        rest = video_dir_name.split("_", 2)[2]
        return f"{subject}_{rest}"
    return f"{subject}_{video_dir_name}"


def seg_id_for_category(cat: str) -> str:
    idx = CATS.index(cat) + 1 if cat in CATS else len(CATS) + 1
    return f"seg_{idx:04d}"


def find_segment_file(cat_dir: Path) -> Optional[Path]:
    mp4s = sorted([p for p in cat_dir.glob("*.mp4") if p.is_file()])
    return mp4s[0] if mp4s else None


def restructure_subject(root: Path, subject: str, dry_run: bool = False) -> List[str]:
    changes: List[str] = []
    subj_dir = root / subject
    if not subj_dir.exists():
        return changes
    for video_dir in sorted([p for p in subj_dir.iterdir() if p.is_dir()]):
        video_id = canonical_video_id(subject, video_dir.name)
        dest_dir = subj_dir / video_id
        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
        # move canonical root files if present
        for seg_idx in range(1, 5):
            seg_id = f"seg_{seg_idx:04d}"
            src_canon = video_dir / f"{video_id}_{seg_id}.mp4"
            if src_canon.exists():
                dest_canon = dest_dir / src_canon.name
                if src_canon != dest_canon:
                    if not dry_run:
                        try:
                            shutil.move(str(src_canon), str(dest_canon))
                        except Exception as e:
                            logger.error("Move failed %s -> %s: %s", src_canon, dest_canon, e)
        for cat in CATS:
            cat_dir = video_dir / cat
            if not cat_dir.exists():
                # not an error if already canonicalized
                continue
            src_file = find_segment_file(cat_dir)
            if not src_file:
                continue
            seg_id = seg_id_for_category(cat)
            dest_file = dest_dir / f"{video_id}_{seg_id}.mp4"
            changes.append(f"MOVE {src_file} -> {dest_file}")
            if not dry_run:
                try:
                    shutil.move(str(src_file), str(dest_file))
                except Exception as e:
                    logger.error("Move failed %s -> %s: %s", src_file, dest_file, e)
        # Optionally cleanup empty category dirs
        if not dry_run:
            for cat in CATS:
                cat_dir = video_dir / cat
                try:
                    if cat_dir.exists() and not any(cat_dir.iterdir()):
                        cat_dir.rmdir()
                except Exception:
                    pass
            # Remove original video_dir if empty
            try:
                if video_dir.exists() and not any(video_dir.iterdir()):
                    video_dir.rmdir()
            except Exception:
                pass
    return changes


def run(segments_root: Path, subjects: Optional[List[str]], dry_run: bool) -> None:
    subs = subjects or [
        "biology",
        "chemistry",
        "chinese",
        "english",
        "geography",
        "history",
        "math",
        "physics",
        "politics",
        "tech",
    ]
    for subj in subs:
        changes = restructure_subject(segments_root, subj, dry_run=dry_run)
        for ch in changes:
            logger.info(ch)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restructure segments_videos to canonical layout")
    parser.add_argument(
        "--segments-root",
        type=Path,
        default=Path("data/segments_videos"),
        help="Root of segments_videos",
    )
    parser.add_argument(
        "--subjects",
        type=str,
        nargs="*",
        default=None,
        help="Subjects to process (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print planned changes without moving files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(args.segments_root, args.subjects, args.dry_run)


if __name__ == "__main__":
    main()