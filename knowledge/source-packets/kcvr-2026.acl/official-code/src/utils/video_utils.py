from __future__ import annotations

import logging
import math
import subprocess
from pathlib import Path
from typing import List, Optional


logger = logging.getLogger(__name__)


def ensure_dir(path: Path) -> None:
    """Ensure a directory exists.

    Args:
        path: Directory path to create if missing.

    Returns:
        None

    Raises:
        OSError: If directory cannot be created.
    """
    path.mkdir(parents=True, exist_ok=True)


def _extract_with_cv2(video_path: Path, targets: List[Path], timestamps: List[float]) -> bool:
    try:
        import cv2  # type: ignore
    except Exception as e:
        logger.warning("OpenCV not available: %s", e)
        return False

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.warning("Failed to open video via OpenCV: %s", video_path)
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps and fps > 0 else 0.0
    if duration <= 0 or frame_count <= 0:
        logger.warning("Invalid video metadata (fps/frame_count): %s", video_path)
        cap.release()
        return False

    for t, out in zip(timestamps, targets):
        frame_idx = int(min(max(round(t * fps), 0), frame_count - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok or frame is None:
            logger.warning("Failed to decode frame at %.3fs in %s", t, video_path)
            cap.release()
            return False
        ensure_dir(out.parent)
        cv2.imwrite(str(out), frame)

    cap.release()
    return True


def _extract_with_ffmpeg(video_path: Path, targets: List[Path], timestamps: List[float]) -> bool:
    ffmpeg = "ffmpeg"
    ok = True
    for t, out in zip(timestamps, targets):
        ensure_dir(out.parent)
        cmd = [
            ffmpeg,
            "-y",
            "-ss",
            f"{t:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(out),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.warning("ffmpeg extract failed at %.3fs for %s: %s", t, video_path, e)
            ok = False
            break
    return ok


def extract_uniform_frames(
    video_path: Path,
    out_dir: Path,
    num_frames: int = 8,
    method: str = "center",
) -> List[Path]:
    """Extract uniformly distributed frames from a video.

    Args:
        video_path: Input video file path.
        out_dir: Output directory for frames.
        num_frames: Number of frames to extract (default: 8).
        method: "center" or "linspace" timestamp sampling.

    Returns:
        List of output frame paths ordered 0..num_frames-1.

    Raises:
        FileNotFoundError: If video_path does not exist.
        RuntimeError: If frame extraction fails.
    """
    if not video_path.exists():
        raise FileNotFoundError(str(video_path))

    ensure_dir(out_dir)
    targets = [out_dir / f"{i:03d}.jpg" for i in range(num_frames)]

    # Probe video duration using OpenCV first to compute timestamps
    dur: Optional[float] = None
    fps: Optional[float] = None
    frame_count: Optional[int] = None
    try:
        import cv2  # type: ignore
        cap = cv2.VideoCapture(str(video_path))
        if cap.isOpened():
            fps_val = cap.get(cv2.CAP_PROP_FPS)
            fc_val = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = fps_val if fps_val and fps_val > 0 else None
            frame_count = fc_val if fc_val and fc_val > 0 else None
            if fps and frame_count:
                dur = frame_count / fps
        cap.release()
    except Exception:
        pass

    if dur and dur > 0:
        if method == "center":
            timestamps = [((i + 0.5) / num_frames) * dur for i in range(num_frames)]
        else:
            timestamps = [(i / (num_frames - 1)) * dur for i in range(num_frames)]
    else:
        # Fallback to linspace over an assumed duration of 1.0s; ffmpeg will seek safely
        timestamps = [i / max(num_frames - 1, 1) for i in range(num_frames)]

    if _extract_with_cv2(video_path, targets, timestamps):
        return targets

    if _extract_with_ffmpeg(video_path, targets, timestamps):
        return targets

    raise RuntimeError(f"Failed to extract frames: {video_path}")


def subject_order() -> List[str]:
    """Return canonical subject order.

    Args:
        None

    Returns:
        List of subject names.
    """
    return [
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


def canonical_segment_names() -> List[str]:
    """Return canonical segment category names in order.

    Args:
        None

    Returns:
        List of category names.
    """
    return ["intro", "exposition", "interaction", "conclusion"]