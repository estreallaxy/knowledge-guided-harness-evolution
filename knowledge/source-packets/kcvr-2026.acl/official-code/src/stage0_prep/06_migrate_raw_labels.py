from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


CANON_SUBJECTS = {
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
}


CN_STAGE_MAP = {
    "导入": "intro",
    "讲授": "exposition",
    "互动": "interaction",
    "总结": "conclusion",
}


def pad3(n: int) -> str:
    return f"{n:03d}"


def parse_subject_dir(name: str) -> Optional[str]:
    if not name.startswith("dataset_"):
        return None
    subj = name.split("_", 1)[1]
    return subj if subj in CANON_SUBJECTS else None


def detect_stage(fname: str) -> Optional[str]:
    for k, v in CN_STAGE_MAP.items():
        if k in fname:
            return v
    parts = fname.split("_")
    for i in range(len(parts) - 1):
        if parts[i].isdigit():
            try:
                idx = int(parts[i + 1])
            except Exception:
                continue
            if idx == 1:
                return "intro"
            if idx == 2:
                return "exposition"
            if idx == 3:
                return "interaction"
            if idx == 4:
                return "conclusion"
    return None


def is_global(fname: str) -> bool:
    return "global" in fname


def is_segments(fname: str) -> bool:
    return "segments" in fname


def is_sentences(fname: str) -> bool:
    return "sentences" in fname


def write_json(dst: Path, data: Dict) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def migrate_subject(src_root: Path, dst_root: Path, subject: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    src_subj = src_root / f"dataset_{subject}"
    if not src_subj.exists():
        return rows
    for video_dir in sorted([p for p in src_subj.iterdir() if p.is_dir()]):
        if not video_dir.name.isdigit():
            continue
        vid_no = int(video_dir.name)
        video_id = pad3(vid_no)
        for jf in sorted(video_dir.glob("*.json")):
            fname = jf.name
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except Exception:
                rows.append(
                    {
                        "src_path": jf.as_posix(),
                        "subject": subject,
                        "video_id": video_id,
                        "target_type": "unknown",
                        "stage": "",
                        "dst_path": "",
                        "status": "json_load_error",
                    }
                )
                continue

            if is_global(fname):
                dst = dst_root / "data/annotations/raw_labels/full_videos" / subject / video_id / f"{subject}_{video_id}_global.json"
                write_json(dst, data)
                rows.append(
                    {
                        "src_path": jf.as_posix(),
                        "subject": subject,
                        "video_id": video_id,
                        "target_type": "global",
                        "stage": "",
                        "dst_path": dst.as_posix(),
                        "status": "ok",
                    }
                )
                continue

            if is_segments(fname):
                dst = dst_root / "data/annotations/raw_labels/full_videos" / subject / video_id / f"{subject}_{video_id}_segments.json"
                write_json(dst, data)
                rows.append(
                    {
                        "src_path": jf.as_posix(),
                        "subject": subject,
                        "video_id": video_id,
                        "target_type": "segments",
                        "stage": "",
                        "dst_path": dst.as_posix(),
                        "status": "ok",
                    }
                )
                continue

            if is_sentences(fname):
                dst = dst_root / "data/annotations/raw_labels/full_videos" / subject / video_id / f"{subject}_{video_id}_sentences.json"
                write_json(dst, data)
                rows.append(
                    {
                        "src_path": jf.as_posix(),
                        "subject": subject,
                        "video_id": video_id,
                        "target_type": "sentences",
                        "stage": "",
                        "dst_path": dst.as_posix(),
                        "status": "ok",
                    }
                )
                continue

            stage = detect_stage(fname)
            if stage is None:
                rows.append(
                    {
                        "src_path": jf.as_posix(),
                        "subject": subject,
                        "video_id": video_id,
                        "target_type": "segment",
                        "stage": "",
                        "dst_path": "",
                        "status": "stage_unknown",
                    }
                )
                continue

            dst = dst_root / "data/annotations/raw_labels/segments" / subject / video_id / f"{subject}_{video_id}_{stage}.json"
            write_json(dst, data)
            rows.append(
                {
                    "src_path": jf.as_posix(),
                    "subject": subject,
                    "video_id": video_id,
                    "target_type": "segment",
                    "stage": stage,
                    "dst_path": dst.as_posix(),
                    "status": "ok",
                }
            )
    return rows


def backup_raw_labels(dst_root: Path, backup_dir: Path) -> None:
    src = dst_root / "data/annotations/raw_labels"
    if not src.exists():
        return
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.make_archive(backup_dir.as_posix(), "zip", src)


def write_csv(rows: List[Dict[str, str]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "src_path",
        "subject",
        "video_id",
        "target_type",
        "stage",
        "dst_path",
        "status",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--src-root", type=Path, default=None, help="Source root directory (required)")
    p.add_argument("--dst-root", type=Path, default=Path("."))
    p.add_argument("--backup", action="store_true")
    p.add_argument("--csv", type=Path, default=Path("experiments/v7.4_run1/raw_labels_migration.csv"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.backup:
        backup_raw_labels(args.dst_root, Path("experiments/v7.4_run1/raw_labels_backup"))
    all_rows: List[Dict[str, str]] = []
    for subj_dir in sorted([p for p in args.src_root.iterdir() if p.is_dir()]):
        subj = parse_subject_dir(subj_dir.name)
        if subj is None:
            continue
        rows = migrate_subject(args.src_root, args.dst_root, subj)
        all_rows.extend(rows)
    write_csv(all_rows, args.csv)
    ok = sum(1 for r in all_rows if r["status"] == "ok")
    bad = sum(1 for r in all_rows if r["status"] != "ok")
    print(f"migrated={ok} issues={bad} total={len(all_rows)} csv={args.csv}")


if __name__ == "__main__":
    main()