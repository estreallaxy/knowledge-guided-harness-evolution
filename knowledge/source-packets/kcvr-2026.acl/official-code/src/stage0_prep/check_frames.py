from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import csv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_segment_frames(video_id: str, segment_id: str, cache_root: Path) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    seg_dir = cache_root / video_id / segment_id
    if not seg_dir.exists():
        errors.append(f"missing_dir:{seg_dir}")
        return False, errors
    files = sorted([p for p in seg_dir.glob("*.jpg") if p.is_file()])
    if len(files) != 8:
        errors.append(f"wrong_count:{len(files)}")
    expected = [seg_dir / f"{i:03d}.jpg" for i in range(8)]
    for p in expected:
        if not p.exists():
            errors.append(f"missing_frame:{p.name}")
    return len(errors) == 0, errors


def check_standard_labels_micro(root: Path, cache_root: Path) -> Dict[str, List[str]]:
    issues: Dict[str, List[str]] = {}
    for subj_dir in sorted((root / "data/annotations/standard_labels/micro").glob("*")):
        if not subj_dir.is_dir():
            continue
        for vid_dir in sorted(subj_dir.glob("*")):
            if not vid_dir.is_dir():
                continue
            video_id = f"{subj_dir.name}_{vid_dir.name}"
            for seg_json in sorted(vid_dir.rglob("*.json")):
                try:
                    data = json.loads(seg_json.read_text(encoding="utf-8"))
                except Exception as e:
                    issues[seg_json.as_posix()] = [f"json_load_error:{e}"]
                    continue
                segment_id = data.get("segment_id")
                paths: List[str] = data.get("image_paths", [])
                if not segment_id or not paths:
                    issues[seg_json.as_posix()] = ["missing_fields:segment_id_or_image_paths"]
                    continue
                ok, errs = check_segment_frames(video_id, segment_id, cache_root)
                if not ok:
                    issues[seg_json.as_posix()] = errs
                else:
                    # also check path existence
                    missing_files = [p for p in paths if not (Path(p)).exists()]
                    if missing_files:
                        issues[seg_json.as_posix()] = [f"missing_paths:{len(missing_files)}"]
    return issues


def resolve_video_id(subject: str, name: str) -> str:
    if "_" in name:
        prefix, rest = name.split("_", 1)
        if prefix == subject:
            return name
    return f"{subject}_{name}"


def check_segments_alignment(segments_root: Path, cache_root: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for subj_dir in sorted(segments_root.glob("*")):
        if not subj_dir.is_dir():
            continue
        subject = subj_dir.name
        for vid_dir in sorted(subj_dir.glob("*")):
            if not vid_dir.is_dir():
                continue
            video_dir_name = vid_dir.name
            video_id = resolve_video_id(subject, video_dir_name)
            for cat, seg_id in (
                ("intro", "seg_0001"),
                ("exposition", "seg_0002"),
                ("interaction", "seg_0003"),
                ("conclusion", "seg_0004"),
            ):
                seg_dir = cache_root / video_id / seg_id
                if not seg_dir.exists():
                    rows.append(
                        {
                            "subject": subject,
                            "video_dir": video_dir_name,
                            "video_id": video_id,
                            "segment_id": seg_id,
                            "check": "cache_dir",
                            "status": "missing",
                            "details": seg_dir.as_posix(),
                        }
                    )
                    continue
                jpgs = sorted(seg_dir.glob("*.jpg"))
                status = "ok" if len(jpgs) == 8 else "wrong_count"
                rows.append(
                    {
                        "subject": subject,
                        "video_dir": video_dir_name,
                        "video_id": video_id,
                        "segment_id": seg_id,
                        "check": "frame_count",
                        "status": status,
                        "details": str(len(jpgs)),
                    }
                )
    return rows


def write_csv(rows: List[Dict[str, str]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "subject",
        "video_dir",
        "video_id",
        "segment_id",
        "check",
        "status",
        "details",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate frames and export CSV report")
    parser.add_argument("--segments-root", type=Path, default=Path("data/segments_videos"))
    parser.add_argument("--cache-root", type=Path, default=Path("cache/frames"))
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("experiments/v7.4_run1/metrics_frames.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = check_segments_alignment(args.segments_root, args.cache_root)
    write_csv(rows, args.output_csv)
    ok_rows = [r for r in rows if r["status"] == "ok"]
    bad_rows = [r for r in rows if r["status"] != "ok"]
    print(
        f"Report written: {args.output_csv} | ok={len(ok_rows)} bad={len(bad_rows)} total={len(rows)}"
    )


if __name__ == "__main__":
    main()