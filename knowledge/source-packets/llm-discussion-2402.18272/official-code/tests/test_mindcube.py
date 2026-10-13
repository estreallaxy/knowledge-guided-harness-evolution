import io
import json
from pathlib import Path
import re
import zipfile

import httpx
import pytest

from llm_discussion.benchmarks import mindcube


def _fixture(monkeypatch, *, broken_viewer=False, ignore_ranges=False):
    rows = [{"id": f"{category}_group0_q{i}",
             "question": "What is on the left? A. Chair B. Table",
             "images": [f"other_all_image/{category}/scene/view.png"],
             "gt_answer": "B", "reasoning_chain": "PRIVATE GOLD REASONING"}
            for category in ("among", "rotation", "around") for i in range(2)]
    images = {name: ("image-" + name).encode() for row in rows for name in row["images"]}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in mindcube.SPLITS.values():
            archive.writestr("data/raw/" + name, "\n".join(json.dumps(r) for r in rows))
        for name, data in images.items():
            archive.writestr("data/" + name, data)
    packed = buffer.getvalue()
    calls = []

    def respond(request):
        calls.append(request)
        if str(request.url) == mindcube.ARCHIVE_URL:
            if ignore_ranges:
                return httpx.Response(200, content=packed)
            match = re.fullmatch(r"bytes=(\d+)-(\d+)", request.headers["Range"])
            start, end = map(int, match.groups())
            return httpx.Response(206, content=packed[start:end + 1],
                                  headers={"Content-Range": f"bytes {start}-{end}/{len(packed)}"})
        name = str(request.url).removeprefix(mindcube.VIEWER_URL)
        return httpx.Response(200, content=b"stale-image" if broken_viewer else images[name])

    monkeypatch.setattr(mindcube, "ARCHIVE_SIZE", len(packed))
    monkeypatch.setattr(mindcube, "_client", lambda: httpx.Client(transport=httpx.MockTransport(respond)))
    return rows, images, calls


def test_prepare_balanced_subset_has_local_images_and_no_gold_reasoning(tmp_path, monkeypatch):
    _, images, _ = _fixture(monkeypatch)
    path = mindcube.prepare(tmp_path, limit=3)
    tasks = [json.loads(line) for line in path.read_text().splitlines()]
    assert [task["category"] for task in tasks] == ["among", "rotation", "around"]
    assert all(task["options"] == ["Chair", "Table"] for task in tasks)
    assert all(task["reference"] == "B" and task["answer_type"] == "choice" for task in tasks)
    assert all(task["question"] == "What is on the left?" for task in tasks)
    assert "PRIVATE GOLD REASONING" not in path.read_text()
    for task in tasks:
        assert not Path(task["images"][0]).is_absolute()
        source = task["images"][0].replace("images/", "other_all_image/", 1)
        assert (tmp_path / task["images"][0]).read_bytes() == images[source]
    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert provenance["source_tasks"] == 6 and provenance["prepared_tasks"] == 3
    assert provenance["revision"] == mindcube.REVISION
    assert provenance["evaluation_split"] is True
    assert provenance["license"] == "MIT"


def test_stale_viewer_images_fall_back_to_pinned_archive(tmp_path, monkeypatch):
    _, images, calls = _fixture(monkeypatch, broken_viewer=True)
    mindcube.prepare(tmp_path, limit=1)
    assert (tmp_path / "images/among/scene/view.png").read_bytes() == images["other_all_image/among/scene/view.png"]
    assert any(str(call.url).startswith(mindcube.VIEWER_URL) for call in calls)


def test_completed_cache_needs_no_network_and_corruption_is_repaired(tmp_path, monkeypatch):
    _, images, calls = _fixture(monkeypatch)
    mindcube.prepare(tmp_path, limit=1)
    calls.clear()
    mindcube.prepare(tmp_path, limit=1)
    assert calls == []
    target = tmp_path / "images/among/scene/view.png"
    target.write_bytes(b"corrupted")
    mindcube.prepare(tmp_path, limit=1)
    assert target.read_bytes() == images["other_all_image/among/scene/view.png"]
    assert len(calls) == 1


def test_full_corpus_is_not_marked_as_holdout(tmp_path, monkeypatch):
    _fixture(monkeypatch)
    path = mindcube.prepare(tmp_path, split="full")
    assert len(path.read_text().splitlines()) == 6
    assert json.loads((tmp_path / "provenance.json").read_text())["evaluation_split"] is False


def test_archive_range_is_required_before_reading_entire_response(tmp_path, monkeypatch):
    _fixture(monkeypatch, ignore_ranges=True)
    with pytest.raises(ValueError, match="did not honor"):
        mindcube.prepare(tmp_path)
    assert not (tmp_path / "tasks.jsonl").exists()


@pytest.mark.parametrize("kwargs", [{"split": "train"}, {"limit": 0}, {"limit": True}])
def test_invalid_selection_fails_without_network(tmp_path, monkeypatch, kwargs):
    monkeypatch.setattr(mindcube, "_client", lambda: pytest.fail("unexpected network client"))
    with pytest.raises(ValueError):
        mindcube.prepare(tmp_path, **kwargs)


def test_noncanonical_option_order_keeps_original_answer_letters():
    row = {"id": "aroundnew_group0_q1", "question": "Which? A. First C. Third B. Second",
           "images": ["other_all_image/around/x.png"], "gt_answer": "C"}
    task = mindcube._task(row)
    assert task["options"] == ["First", "Second", "Third"]
    assert task["reference"] == "C" and task["category"] == "around"


def test_image_path_cannot_escape_output():
    with pytest.raises(ValueError, match="Invalid MindCube image path"):
        mindcube._image_path("other_all_image/../../outside.png")
