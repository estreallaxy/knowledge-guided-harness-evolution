import asyncio
from dataclasses import asdict, replace
import json

import pytest

from llm_discussion.answers import normalize_answer, parse_answer
from llm_discussion.data import load_tasks
from llm_discussion.engine import run_discussion
from llm_discussion.models import DryRunModel
from llm_discussion.prompts import QUESTION, SYSTEM, UPDATE, discussion_request
from llm_discussion.types import DiscussionConfig, Task


@pytest.mark.parametrize("raw, expected", [('"A"', "A"), ('" b "', "B"), ('"c"', "C")])
def test_choice_answer_is_normalized_from_explicit_json(raw, expected):
    answer = parse_answer('{"reasons":"evidence", "answer":' + raw + '}', "choice", ("A", "B", "C"))
    assert answer.value == expected


@pytest.mark.parametrize("raw", ['"D"', '"Option A"', '"(A)"', '"A or B"', '""', '1', 'true', 'null'])
def test_choice_parser_rejects_guesses_and_unknown_options(raw):
    with pytest.raises(ValueError):
        parse_answer('{"answer":' + raw + '}', "choice", ("A", "B", "C"))


def test_generic_loader_resolves_images_and_validates_choice_gold(tmp_path):
    images = tmp_path / "frames"
    images.mkdir()
    (images / "one.png").write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    path = tmp_path / "tasks.jsonl"
    path.write_text(json.dumps({
        "id": "spatial-1", "question": "Which object is to the left?", "answer_type": "choice",
        "options": ["chair", "table"], "answer": "b", "category": "relative_direction",
        "images": ["frames/one.png", "https://example.com/frame-two.png"],
    }))
    task, = load_tasks(path)
    assert task.reference == "B"
    assert task.choices == ("A", "B")
    assert task.options == ("chair", "table")
    assert task.category == "relative_direction"
    assert task.images == (str(images / "one.png"), "https://example.com/frame-two.png")


@pytest.mark.parametrize("override", [
    {"options": ["one"]}, {"options": ["one", ""]}, {"options": "one, two"},
    {"reference": "C"}, {"answer_type": "unknown"}, {"category": 1},
    {"metric": "mra"}, {"images": "frame.png"}, {"images": ["data:image/png;base64,secret"]},
    {"images": ["missing.png"]},
])
def test_invalid_multimodal_data_fails_before_execution(tmp_path, override):
    record = {"question": "q", "answer_type": "choice", "options": ["one", "two"], "reference": "A"}
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps(record | override))
    with pytest.raises(ValueError):
        load_tasks(path)


def test_all_rounds_and_secretary_see_images_but_never_reference():
    task = Task("spatial", "Which object is nearer?", "C",
                ("/absolute/frame-1.png", "https://example.com/frame-2.jpg"),
                ("chair", "table", "lamp"), "choice", "relative_distance")

    class PrivateReasonModel(DryRunModel):
        async def generate(self, request):
            answer = json.loads(await super().generate(request))
            answer["reasons"] = f"private-{request.agent_id}-round-{request.round}"
            return json.dumps(answer)

    first = asyncio.run(run_discussion(task, PrivateReasonModel("tie")))
    second = asyncio.run(run_discussion(replace(task, reference="B"), PrivateReasonModel("tie")))
    assert first.status == "completed"
    assert first.calls == second.calls  # Changing the gold cannot affect any model request.
    assert first.answer_type == "choice"
    assert first.category == "relative_distance"
    assert first.votes == {"A": 3, "B": 3}
    assert first.used_secretary
    for call in first.calls:
        request = call.request
        assert request.answer_type == "choice"
        assert request.choices == ("A", "B", "C")
        image_messages = [m for m in request.messages if isinstance(m.content, list)]
        assert len(image_messages) == 1
        parts = image_messages[0].content
        assert parts[0]["type"] == "text"
        assert task.question in parts[0]["text"]
        assert "A. chair" in parts[0]["text"]
        assert tuple(p["image_url"]["url"] for p in parts[1:]) == task.images
        assert "grade school" not in json.dumps(asdict(request))
        if request.stage == "discussion" and request.round > 1:
            peers = request.messages[3].content
            own_group = "ABC" if request.agent_id in "ABC" else "DEF"
            for agent in "ABCDEF":
                visible = agent in own_group and agent != request.agent_id
                assert (f"private-{agent}-round-{request.round - 1}" in peers) == visible
    secretary = first.calls[-1].request
    assert "private-A-round-3" in secretary.messages[0].content
    assert "private-D-round-3" in secretary.messages[0].content
    assert "private-B-round-3" not in secretary.messages[0].content


def test_visual_numeric_tasks_keep_numeric_output_and_metric():
    task = Task("distance", "Estimate the distance.", "2", ("https://example.com/room.png",),
                answer_type="number", category="absolute_distance", metric="mra")
    result = asyncio.run(run_discussion(task, DryRunModel(), DiscussionConfig(agents=1, group_size=1, rounds=1)))
    assert result.status == "completed"
    assert result.metric == "mra"
    assert result.answer_type == "number"
    assert "grade school" not in str(result.calls[0].request.messages)
    assert normalize_answer(result.answer) == result.answer


def test_text_gsm8k_prompts_keep_original_exact_wording():
    task = Task("gsm8k", "What is 2 plus 3?")
    request = discussion_request(task, "A", 1, (), DiscussionConfig())
    assert request.messages[0].content == SYSTEM
    assert request.messages[1].content == QUESTION.replace("<question>", task.question) + "\n"
    result = asyncio.run(run_discussion(task, DryRunModel()))
    updated = result.calls[6].request
    assert updated.messages[1].content == QUESTION.replace("<question>", task.question)
    assert updated.messages[-1].content == UPDATE
