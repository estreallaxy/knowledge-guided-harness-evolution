from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from src.utils.video_utils import (
    canonical_segment_names,
    extract_uniform_frames,
    subject_order,
)


logger = logging.getLogger(__name__)


def find_segment_video(video_dir: Path, video_id: str, seg_id: str, category: str) -> Optional[Path]:
    """Find segment mp4 in canonical location or fallback to category dir.

    Args:
        video_dir: Directory representing the video.
        video_id: Canonical video id (e.g., biology_001).
        seg_id: Segment id (e.g., seg_0001).
        category: Category name (intro/exposition/interaction/conclusion).

    Returns:
        The mp4 file path if found, else None.
    """
    # Prefer canonical filename at video_dir root
    canonical = video_dir / f"{video_id}_{seg_id}.mp4"
    if canonical.exists():
        return canonical
    # Fallback: search in category subdir
    cat_dir = video_dir / category
    if not cat_dir.exists() or not cat_dir.is_dir():
        return None
    mp4s = sorted([p for p in cat_dir.glob("*.mp4") if p.is_file()])
    return mp4s[0] if mp4s else None


def resolve_video_id(subject: str, video_dir: Path) -> str:
    name = video_dir.name
    if "_" in name:
        prefix, rest = name.split("_", 1)
        if prefix == subject:
            return name
    return f"{subject}_{name}"


def category_to_seg_id(category: str, order: Optional[List[str]] = None) -> str:
    """Convert category name to canonical segment_id.

    Args:
        category: Category name (e.g., "intro").
        order: Category order list; defaults to canonical order.

    Returns:
        Segment ID like "seg_0001".
    """
    categories = order or canonical_segment_names()
    try:
        idx = categories.index(category) + 1
    except ValueError:
        idx = len(categories) + 1
    return f"seg_{idx:04d}"


def iter_subject_videos(root: Path, subject: str) -> Iterable[Path]:
    """Yield per-video directories under a subject.

    Args:
        root: Root of segments_videos.
        subject: Subject name.

    Returns:
        Iterable of video directories.
    """
    subj_dir = root / subject
    if not subj_dir.exists():
        return []
    return [p for p in sorted(subj_dir.iterdir()) if p.is_dir()]


def extract_for_video(
    segments_root: Path,
    subject: str,
    video_dir: Path,
    cache_root: Path,
    overwrite: bool = False,
    method: str = "center",
) -> Dict[str, List[Path]]:
    """Extract 8 frames for the four canonical segments of a video.

    Args:
        segments_root: Root directory of segments_videos.
        subject: Subject name.
        video_dir: Directory representing this video (e.g., "001").
        cache_root: Root directory to store frames (e.g., cache/frames).
        overwrite: Whether to overwrite existing frames.
        method: Timestamp sampling method ("center" or "linspace").

    Returns:
        Mapping from segment_id to list of output frame paths.

    Raises:
        RuntimeError: If any required segment video is missing or extraction fails.
    """
    video_id = resolve_video_id(subject, video_dir)
    categories = canonical_segment_names()
    out_map: Dict[str, List[Path]] = {}
    for cat in categories:
        seg_id = category_to_seg_id(cat, categories)
        vid = find_segment_video(video_dir=video_dir, video_id=video_id, seg_id=seg_id, category=cat)
        if vid is None:
            logger.warning("Missing segment video: %s / %s", video_id, cat)
            # Skip this segment, continue with others
            continue

        out_dir = cache_root / video_id / seg_id
        frames = [out_dir / f"{i:03d}.jpg" for i in range(8)]
        if not overwrite and all(p.exists() for p in frames):
            out_map[seg_id] = frames
            continue

        extracted = extract_uniform_frames(vid, out_dir, num_frames=8, method=method)
        out_map[seg_id] = extracted

    return out_map


def run(
    segments_root: Path,
    cache_root: Path,
    subjects: Optional[List[str]] = None,
    limit_videos: Optional[int] = None,
    overwrite: bool = False,
    method: str = "center",
) -> None:
    """Run extraction across subjects and videos.

    Args:
        segments_root: Root of segments_videos.
        cache_root: Root for frame cache output.
        subjects: Subjects to process, default to canonical order.
        limit_videos: Optional limit per subject.
        overwrite: Overwrite existing frames.
        method: Timestamp sampling method.

    Returns:
        None
    """
    subs = subjects or subject_order()
    for subj in subs:
        vids = list(iter_subject_videos(segments_root, subj))
        if limit_videos is not None:
            vids = vids[: max(limit_videos, 0)]
        for vdir in vids:
            try:
                extract_for_video(
                    segments_root=segments_root,
                    subject=subj,
                    video_dir=vdir,
                    cache_root=cache_root,
                    overwrite=overwrite,
                    method=method,
                )
            except Exception as e:
                logger.error("Extraction failed for %s/%s: %s", subj, vdir.name, e)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract 8 frames per segment video")
    parser.add_argument(
        "--segments-root",
        type=Path,
        default=Path("data/segments_videos"),
        help="Root directory of segments videos",
    )
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path("cache/frames"),
        help="Root for output frames",
    )
    parser.add_argument(
        "--subjects",
        type=str,
        nargs="*",
        default=None,
        help="Subjects to process (default: all)",
    )
    parser.add_argument(
        "--limit-videos",
        type=int,
        default=None,
        help="Limit number of videos per subject",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing frames",
    )
    parser.add_argument(
        "--method",
        type=str,
        default="center",
        choices=["center", "linspace"],
        help="Timestamp sampling method",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    subjects = args.subjects or subject_order()
    run(
        segments_root=args.segments_root,
        cache_root=args.cache_root,
        subjects=subjects,
        limit_videos=args.limit_videos,
        overwrite=args.overwrite,
        method=args.method,
    )


if __name__ == "__main__":
    main()