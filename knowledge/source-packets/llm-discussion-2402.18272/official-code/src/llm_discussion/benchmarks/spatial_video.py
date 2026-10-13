"""Prepare SAW-Bench videos as explicitly budgeted, ordered image frames.

The fixed frame budget is our evaluation protocol. The published SAW-Bench
leaderboard usually samples at 2 fps, so the protocols must be labeled separately.
VSI-Bench is not implemented: it also needs numerical MRA and task-macro scoring.
"""

import hashlib
import json
import logging
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Semaphore
from urllib.request import urlopen


SAW_REPO = "ucsbai/SAW-Bench"
SAW_REVISION = "6d74dc33e1357bc57974092ada8c79623db9bf50"
SAW_METADATA_SHA256 = "06a4d84c35fabfed18abaa919e565aecf180b41d3664970f9761eb37fcaf8f72"
VIDEO_FRAME_INSTRUCTION = "The images are uniformly sampled frames from one video, in chronological order."
_TASKS = {"localization", "direction", "shape", "revplan", "memory", "affordance"}
_LOGGER = logging.getLogger(__name__)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, destination: Path, expected_hash: str | None = None) -> str:
    """Cache public assets atomically; a sidecar detects corrupt partial caches."""
    sidecar = destination.with_suffix(destination.suffix + ".sha256")
    if destination.exists():
        digest = _sha256(destination)
        saved = sidecar.read_text().strip() if sidecar.exists() else None
        if digest == (expected_hash or saved):
            return digest
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    try:
        with urlopen(url, timeout=120) as response, partial.open("wb") as stream:
            for chunk in iter(lambda: response.read(1024 * 1024), b""):
                stream.write(chunk)
        digest = _sha256(partial)
        if expected_hash is not None and digest != expected_hash:
            raise ValueError("Downloaded SAW metadata SHA-256 does not match the pinned source")
        partial.replace(destination)
        sidecar.write_text(digest + "\n")
        return digest
    finally:
        partial.unlink(missing_ok=True)


def _read_parquet(path: Path) -> list[dict]:
    try:
        import pyarrow.parquet as parquet
    except ImportError:
        raise ValueError("Dataset preparation requires: pip install 'llm-discussion[benchmarks]'") from None
    return parquet.read_table(path).to_pylist()


def _sample_video(video: Path, destination: Path, frames: int, video_hash: str) -> list[Path]:
    marker = destination / "sampling.json"
    if marker.exists():
        saved = json.loads(marker.read_text())
        paths = [destination / name for name in saved.get("frames", {})]
        if (saved.get("video_sha256") == video_hash and saved.get("requested_frames") == frames
                and paths and all(p.is_file() and _sha256(p) == saved["frames"][p.name] for p in paths)):
            return paths
    # MP4 metadata normally has an exact frame count; only decode to count when
    # it is absent, avoiding a redundant full decode for each dataset clip.
    probe_command = ["ffprobe", "-v", "error", "-select_streams", "v:0"]
    probe = subprocess.run(probe_command + [
        "-show_entries", "stream=nb_frames", "-of", "json", str(video),
    ], capture_output=True, text=True, timeout=600)
    try:
        total = int(json.loads(probe.stdout)["streams"][0]["nb_frames"])
    except (ValueError, KeyError, IndexError, TypeError):
        probe = subprocess.run(probe_command + [
            "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "json", str(video),
        ], capture_output=True, text=True, timeout=600)
        try:
            total = int(json.loads(probe.stdout)["streams"][0]["nb_read_frames"])
        except (ValueError, KeyError, IndexError, TypeError):
            total = 0
    try:
        if probe.returncode or total < 1:
            raise ValueError
    except ValueError:
        raise ValueError(f"Cannot decode SAW video {video.name}") from None
    count = min(frames, total)
    # Match uniformly spaced frame indices, including the first and last frame.
    indices = [i * (total - 1) // (count - 1) for i in range(count)] if count > 1 else [0]
    destination.mkdir(parents=True, exist_ok=True)
    expression = "+".join(f"eq(n\\,{index})" for index in indices)
    result = subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(video),
        "-vf", f"select={expression}", "-vsync", "0", "-frames:v", str(count),
        "-q:v", "2", "-start_number", "0", str(destination / "frame-%04d.jpg"),
    ], capture_output=True, text=True, timeout=600)
    paths = [destination / f"frame-{i:04d}.jpg" for i in range(count)]
    if result.returncode or not all(p.is_file() and p.stat().st_size for p in paths):
        raise ValueError(f"Cannot sample frames from SAW video {video.name}")
    marker.write_text(json.dumps({
        "video_sha256": video_hash, "requested_frames": frames,
        "source_frame_count": total, "selected_indices": indices,
        "frames": {p.name: _sha256(p) for p in paths},
    }, indent=2) + "\n")
    return paths


def prepare_saw(output: Path, *, limit: int | None = None, frames: int = 32) -> Path:
    """Prepare selected questions; cache full annotations and only needed videos.

    With no limit, prepare all 2,071 questions. Repeated questions sharing a clip
    reuse both downloads and frames. This can download approximately 3.3 GB;
    use ``limit`` for a small smoke run. Gold answers never enter image filenames.
    """
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("limit must be a positive integer or null")
    if type(frames) is not int or frames < 1:
        raise ValueError("frames must be a positive integer")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise ValueError("SAW preparation requires ffmpeg and ffprobe on PATH")
    output = Path(output).resolve()
    base_url = f"https://huggingface.co/datasets/{SAW_REPO}/resolve/{SAW_REVISION}"
    metadata = output / "source" / f"saw-{SAW_REVISION}.parquet"
    metadata_hash = _download(f"{base_url}/data/all.parquet", metadata, SAW_METADATA_SHA256)
    rows = _read_parquet(metadata)
    if len(rows) != 2071:
        raise ValueError("Pinned SAW annotations must contain exactly 2,071 questions")
    selected = rows[:limit] if limit is not None else rows
    tasks, assets = [], {}
    for row in selected:
        key, category = row.get("key"), row.get("task")
        options, answer = row.get("options"), row.get("answer")
        question, index = row.get("question"), row.get("id")
        if (not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9-]+_[A-Za-z0-9_-]+", key)
                or category not in _TASKS or type(index) is not int
                or not isinstance(question, str) or not question.strip()
                or not isinstance(options, list) or not 2 <= len(options) <= 26
                or any(not isinstance(option, str) or not option.strip() for option in options)
                or type(answer) is not int or not 0 <= answer < len(options)
                or options[answer] != row.get("ground_truth")):
            raise ValueError("Unexpected SAW annotation schema or inconsistent answer")
    # This is a bounded preparation pipeline for blocking file I/O and ffmpeg.
    # Model generation uses native async elsewhere; these workers never call a model.
    sampling_slots = Semaphore(2)

    def prepare_video(key: str) -> tuple[str, dict]:
        scene = key.split("_", 1)[0]
        video_url = f"{base_url}/videos_compressed/Scene_{scene}/{key}.mp4"
        video = output / "videos" / SAW_REVISION / f"{key}.mp4"
        video_hash = _download(video_url, video)
        frame_dir = output / "frames" / SAW_REVISION / key / f"uniform-{frames}"
        with sampling_slots:
            paths = _sample_video(video, frame_dir, frames, video_hash)
        return key, {
            "source_url": video_url, "video_sha256": video_hash,
            "video_path": video.relative_to(output).as_posix(),
            "images": [p.relative_to(output).as_posix() for p in paths],
            "sampling_manifest": (frame_dir / "sampling.json").relative_to(output).as_posix(),
        }

    keys = list(dict.fromkeys(row["key"] for row in selected))
    with ThreadPoolExecutor(max_workers=4) as executor:
        pending = [executor.submit(prepare_video, key) for key in keys]
        try:
            for index, future in enumerate(as_completed(pending), 1):
                key, asset = future.result()
                assets[key] = asset
                if index == 1 or index % 10 == 0 or index == len(keys):
                    _LOGGER.info("SAW prepared %d/%d videos", index, len(keys))
        except BaseException:
            for future in pending:
                future.cancel()
            raise
    assets = {key: assets[key] for key in keys}
    for row in selected:
        key, category, index = row["key"], row["task"], row["id"]
        tasks.append({
            "id": f"saw-{category}-{index}",
            "question": VIDEO_FRAME_INSTRUCTION + "\n\n" + row["question"],
            "reference": chr(ord("A") + row["answer"]), "answer_type": "choice",
            "options": row["options"], "images": assets[key]["images"], "category": category,
        })
    if len({row["id"] for row in tasks}) != len(tasks):
        raise ValueError("SAW source contains duplicate question IDs")
    tasks_path = output / "tasks.jsonl"
    tasks_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in tasks), encoding="utf-8")
    (output / "provenance.json").write_text(json.dumps({
        "dataset": "SAW-Bench", "source_repo": SAW_REPO, "source_revision": SAW_REVISION,
        "source_url": f"{base_url}/data/all.parquet", "source_config": "all", "source_split": "test",
        "license": "cc-by-nc-4.0", "metadata_sha256": metadata_hash,
        "metadata_path": metadata.relative_to(output).as_posix(),
        "available_tasks": len(rows), "prepared_tasks": len(tasks),
        "available_videos_in_annotations": len({row["key"] for row in rows}),
        "prepared_videos": len(assets), "selection": {"limit": limit, "order": "source order"},
        "sampling": {"method": "uniform_frame_indices", "requested_frames": frames, "audio": False,
                     "note": "Fixed frame budget; not the published default 2 fps protocol."},
        "prompt_adaptation": {"prefix": VIDEO_FRAME_INSTRUCTION, "original_question": "preserved verbatim after prefix"},
        "metric": "choice_accuracy", "tasks_sha256": _sha256(tasks_path), "assets": assets,
    }, indent=2) + "\n", encoding="utf-8")
    return tasks_path
