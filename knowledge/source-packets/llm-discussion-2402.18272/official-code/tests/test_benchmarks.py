import hashlib
import io
import json
import shutil
import subprocess
import threading
import time

import pytest

from llm_discussion.benchmarks import matharena, spatial_video


@pytest.fixture
def aime_source(monkeypatch):
    pa = pytest.importorskip("pyarrow")
    parquet = pytest.importorskip("pyarrow.parquet")
    rows = [{"problem_idx": i, "problem": f"Competition problem {i}", "answer": i,
             "problem_type": ["Number Theory"]} for i in range(1, 31)]
    sink = pa.BufferOutputStream()
    parquet.write_table(pa.Table.from_pylist(rows), sink)
    content = sink.getvalue().to_pybytes()
    digest = hashlib.sha256(content).hexdigest()
    monkeypatch.setattr(matharena, "_SOURCES", {2025: ("test-revision", digest)})
    calls = []

    def open_metadata(url, **kwargs):
        calls.append(url)
        return io.BytesIO(content)

    monkeypatch.setattr(matharena, "urlopen", open_metadata)
    return calls, digest


def test_aime_full_preparation_preserves_questions_and_source_provenance(tmp_path, aime_source):
    calls, digest = aime_source
    path = matharena.prepare_aime(tmp_path)
    tasks = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(tasks) == 30
    assert tasks[0] == {"id": "aime-2025-1", "question": "Competition problem 1", "reference": "1",
                        "answer_type": "number", "options": [], "images": [], "category": "Number Theory"}
    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert provenance["metadata_sha256"] == digest
    assert provenance["license"] == "cc-by-nc-sa-4.0"
    assert provenance["source_revision"] == "test-revision"
    assert provenance["source_split"] == "train"
    assert "/resolve/test-revision/" in calls[0]
    assert provenance["tasks_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_aime_limit_keeps_full_annotations_and_can_resume_from_cache(tmp_path, aime_source):
    calls, _ = aime_source
    path = matharena.prepare_aime(tmp_path, limit=2)
    assert len(path.read_text().splitlines()) == 2
    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert provenance["available_tasks"] == 30
    assert provenance["prepared_tasks"] == 2
    matharena.prepare_aime(tmp_path, limit=3)
    assert len(calls) == 1
    assert len(path.read_text().splitlines()) == 3


def test_aime_corrupt_cache_is_not_silently_trusted(tmp_path, aime_source):
    matharena.prepare_aime(tmp_path, limit=1)
    metadata, = (tmp_path / "source").glob("*.parquet")
    metadata.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="Cached AIME metadata SHA-256"):
        matharena.prepare_aime(tmp_path)


@pytest.mark.parametrize("kwargs", [{"year": 2024}, {"year": True}, {"limit": 0}, {"limit": True}])
def test_aime_rejects_invalid_configuration_before_download(tmp_path, kwargs):
    with pytest.raises(ValueError):
        matharena.prepare_aime(tmp_path, **kwargs)


@pytest.fixture
def saw_source(monkeypatch):
    rows = [{"id": i, "question": f"Where is the target in clip {i}?", "options": ["Left", "Right"],
             "answer": 1, "ground_truth": "Right", "key": "0_0" if i < 2 else "0_1",
             "task": "direction", "scene_category": "outdoor"} for i in range(2071)]
    monkeypatch.setattr(spatial_video.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(spatial_video, "_read_parquet", lambda path: rows)
    downloads, samples = [], []

    def download(url, destination, expected_hash=None):
        downloads.append(url)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"cached asset")
        return hashlib.sha256(destination.read_bytes()).hexdigest()

    def sample(video, destination, frames, video_hash):
        samples.append(video.name)
        destination.mkdir(parents=True, exist_ok=True)
        paths = [destination / f"frame-{i:04d}.jpg" for i in range(frames)]
        for path in paths:
            path.write_bytes(b"mock JPEG")
        (destination / "sampling.json").write_text("{}")
        return paths

    monkeypatch.setattr(spatial_video, "_download", download)
    monkeypatch.setattr(spatial_video, "_sample_video", sample)
    return rows, downloads, samples


def test_saw_selected_videos_are_downloaded_once_and_labels_are_choices(tmp_path, saw_source):
    _, downloads, samples = saw_source
    path = spatial_video.prepare_saw(tmp_path, limit=3, frames=4)
    tasks = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(tasks) == 3
    assert tasks[0]["reference"] == "B"
    assert tasks[0]["answer_type"] == "choice"
    assert tasks[0]["category"] == "direction"
    assert tasks[0]["id"] == "saw-direction-0"
    assert tasks[0]["images"] == tasks[1]["images"]
    assert len(tasks[0]["images"]) == 4
    assert all((tmp_path / image).is_file() for task in tasks for image in task["images"])
    assert len(downloads) == 3  # all annotations, then two distinct clips
    assert sorted(samples) == ["0_0.mp4", "0_1.mp4"]
    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert provenance["available_tasks"] == 2071
    assert provenance["prepared_tasks"] == 3
    assert provenance["prepared_videos"] == 2
    assert provenance["sampling"]["method"] == "uniform_frame_indices"
    assert provenance["license"] == "cc-by-nc-4.0"


def test_saw_without_limit_prepares_all_annotations(tmp_path, saw_source):
    path = spatial_video.prepare_saw(tmp_path, frames=1)
    assert len(path.read_text().splitlines()) == 2071


def test_saw_video_instruction_preserves_frame_order_and_does_not_use_gold(tmp_path, saw_source):
    rows, _, _ = saw_source
    original_question = rows[0]["question"]
    path = spatial_video.prepare_saw(tmp_path, limit=1, frames=4)
    first = json.loads(path.read_text())
    assert first["question"] == spatial_video.VIDEO_FRAME_INSTRUCTION + "\n\n" + original_question
    assert "one video, in chronological order" in first["question"]
    assert "Right" not in first["question"]
    assert [image.rsplit("/", 1)[-1] for image in first["images"]] == [f"frame-{i:04d}.jpg" for i in range(4)]
    rows[0]["answer"], rows[0]["ground_truth"] = 0, "Left"
    path = spatial_video.prepare_saw(tmp_path, limit=1, frames=4)
    changed = json.loads(path.read_text())
    assert first["reference"] == "B" and changed["reference"] == "A"
    assert changed["question"] == first["question"]
    assert changed["images"] == first["images"]
    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert provenance["prompt_adaptation"]["prefix"] == spatial_video.VIDEO_FRAME_INSTRUCTION


def test_saw_parallel_preparation_bounds_decoders_and_preserves_task_order(tmp_path, saw_source, monkeypatch):
    rows, _, _ = saw_source
    for index in range(8):
        rows[index]["key"] = f"0_{index}"
    sample = spatial_video._sample_video
    lock = threading.Lock()
    active = maximum = 0

    def delayed_sample(*args):
        nonlocal active, maximum
        with lock:
            active += 1
            maximum = max(maximum, active)
        try:
            time.sleep(0.02)
            return sample(*args)
        finally:
            with lock:
                active -= 1

    monkeypatch.setattr(spatial_video, "_sample_video", delayed_sample)
    path = spatial_video.prepare_saw(tmp_path, limit=8, frames=1)
    tasks = [json.loads(line) for line in path.read_text().splitlines()]
    assert maximum == 2
    assert [task["id"] for task in tasks] == [f"saw-direction-{i}" for i in range(8)]
    assert all(f"/0_{i}/" in task["images"][0] for i, task in enumerate(tasks))


def test_saw_inconsistent_gold_is_rejected_before_video_download(tmp_path, saw_source):
    rows, downloads, _ = saw_source
    rows[0]["ground_truth"] = "Left"
    with pytest.raises(ValueError, match="inconsistent answer"):
        spatial_video.prepare_saw(tmp_path, limit=1)
    assert len(downloads) == 1


def test_saw_video_keys_cannot_escape_output(tmp_path, saw_source):
    rows, downloads, _ = saw_source
    rows[0]["key"] = "../../outside"
    with pytest.raises(ValueError, match="annotation schema"):
        spatial_video.prepare_saw(tmp_path, limit=1)
    assert len(downloads) == 1


@pytest.mark.parametrize("kwargs", [{"frames": 0}, {"frames": True}, {"limit": 0}, {"limit": True}])
def test_saw_invalid_configuration_fails_before_network(tmp_path, kwargs):
    with pytest.raises(ValueError):
        spatial_video.prepare_saw(tmp_path, **kwargs)


def test_public_asset_cache_checks_hashes_and_recovers_corruption(tmp_path, monkeypatch):
    content = b"the public data"
    calls = []

    def read(url, **kwargs):
        calls.append(url)
        return io.BytesIO(content)

    monkeypatch.setattr(spatial_video, "urlopen", read)
    path = tmp_path / "clip.mp4"
    digest = hashlib.sha256(content).hexdigest()
    assert spatial_video._download("https://example.invalid/clip", path) == digest
    assert spatial_video._download("https://example.invalid/clip", path) == digest
    assert len(calls) == 1
    path.write_bytes(b"damaged")
    assert spatial_video._download("https://example.invalid/clip", path) == digest
    assert len(calls) == 2
    assert not path.with_suffix(".mp4.part").exists()


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="ffmpeg not installed")
def test_frame_sampling_uses_ordered_uniform_indices_and_reuses_cached_images(tmp_path, monkeypatch):
    video = tmp_path / "clip.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc=size=48x32:rate=5", "-t", "1", "-c:v", "mpeg4", str(video)], check=True)
    video_hash = spatial_video._sha256(video)
    frame_dir = tmp_path / "frames"
    paths = spatial_video._sample_video(video, frame_dir, 3, video_hash)
    assert len(paths) == 3
    saved = json.loads((frame_dir / "sampling.json").read_text())
    assert saved["source_frame_count"] == 5
    assert saved["selected_indices"] == [0, 2, 4]
    assert all(path.read_bytes().startswith(b"\xff\xd8") for path in paths)

    def forbidden(*args, **kwargs):
        raise AssertionError("cached frames should not be decoded again")

    monkeypatch.setattr(spatial_video.subprocess, "run", forbidden)
    assert spatial_video._sample_video(video, frame_dir, 3, video_hash) == paths
