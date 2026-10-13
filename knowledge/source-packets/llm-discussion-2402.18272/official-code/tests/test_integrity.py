"""Offline integration checks for saved inputs and shared request accounting."""

import asyncio
from collections import Counter
import json

import httpx
import pytest

from llm_discussion import cli
from llm_discussion.engine import run_discussion
from llm_discussion.reporting import evaluate_suite
from llm_discussion.scheduling import RequestBudget, Schedule, ScheduledModel
from llm_discussion.storage import read_manifest, read_results
from llm_discussion.types import DiscussionConfig, ModelError, Task


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("integrity checks must not read credentials or contact a provider")

    monkeypatch.setattr(cli, "load_dotenv", forbidden)
    monkeypatch.setattr(cli, "OpenRouterModel", forbidden)
    original_client = httpx.AsyncClient
    monkeypatch.setattr(cli.httpx, "AsyncClient", lambda: original_client(
        transport=httpx.MockTransport(forbidden)))


def test_resume_rejects_image_changes_at_the_same_path(tmp_path, capsys):
    image = tmp_path / "frame.png"
    image.write_bytes(b"original fixture image")
    data = tmp_path / "tasks.jsonl"
    data.write_text(json.dumps({"id": "image-task", "question": "Count the objects.",
                               "reference": "2", "images": [image.name]}) + "\n")
    output = tmp_path / "run"
    args = ["run", "--dataset", str(data), "--output", str(output), "--agents", "1",
            "--group-size", "1", "--rounds", "1", "--dry-run"]
    assert cli.main(args) == 0
    old_results = (output / "results.jsonl").read_bytes()
    old_manifest = (output / "manifest.json").read_bytes()
    assert str(image) in read_manifest(output)["image_sha256"]
    image.write_bytes(b"changed fixture image")
    capsys.readouterr()
    assert cli.main(args + ["--resume"]) == 2
    assert "image_sha256 differs" in capsys.readouterr().err
    assert (output / "results.jsonl").read_bytes() == old_results
    assert (output / "manifest.json").read_bytes() == old_manifest


@pytest.fixture
def synthetic_suite(tmp_path):
    config = tmp_path / "suite-config.json"
    config.write_text(json.dumps({"discussion": {"rounds": 1}, "models": [
        {"model": f"fixture/model-{i}"} for i in range(3)]}))
    data = tmp_path / "tasks.jsonl"
    data.write_text(json.dumps({"id": "same-id", "question": "Which object is closer?",
                               "reference": "A", "answer_type": "choice",
                               "options": ["cube", "sphere"]}) + "\n")
    output = tmp_path / "suite"
    assert cli.main(["suite", "--config", str(config), "--dataset", str(data),
                     "--dry-run", "--output", str(output)]) == 0
    return output


@pytest.mark.parametrize("field,replacement", [
    ("dataset_sha256", "different-dataset-with-the-same-task-id"),
    ("image_sha256", {"frame.png": "changed-image-content"}),
    ("prompts_sha256", "different-prompt"),
    ("sampling", {"seed": 12345, "index": None}),
    ("synthetic", False),
    ("task_ids", ["different-id"]),
])
def test_suite_rejects_a_mismatched_child_manifest(synthetic_suite, field, replacement):
    child = synthetic_suite / "cmd-mixed" / "manifest.json"
    manifest = json.loads(child.read_text())
    manifest[field] = replacement
    child.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match=f"Suite {field} differs"):
        evaluate_suite(synthetic_suite)


def test_default_mixed_model_rate_limit_only_waits_for_free_requests(tmp_path, monkeypatch):
    config = tmp_path / "mixed.json"
    config.write_text(json.dumps({
        "discussion": {"rounds": 1, "max_attempts": 2},
        "model": {"model": "fixture/paid"},
        "agent_models": {agent: {"model": "fixture/free:free"} for agent in "BE"},
        "secretary_model": {"model": "fixture/free:free"},
    }))
    waits = Counter()
    calls = []
    attempts = Counter()

    async def observe_wait(delay):
        waits[asyncio.current_task()] += 1

    class Provider:
        def __init__(self, profile, *, client):
            self.name = profile.model

        async def generate(self, request):
            attempts[request.agent_id] += 1
            calls.append((self.name, request.agent_id, request.stage,
                          waits.pop(asyncio.current_task(), 0)))
            if request.agent_id in "ABG" and attempts[request.agent_id] == 1:
                return "malformed fixture response"
            answer = "1" if request.agent_id in "ABCG" else "2"
            return json.dumps({"reasons": "fixture", "answer": answer})

    monkeypatch.setattr(asyncio, "sleep", observe_wait)
    monkeypatch.setattr(cli, "OpenRouterModel", Provider)
    monkeypatch.setattr(cli, "load_dotenv", lambda *args, **kwargs: None)
    output = tmp_path / "run"
    assert cli.main(["run", "--config", str(config), "--output", str(output)]) == 0
    assert len(calls) == 10  # Six opinions, secretary, and three parse retries.
    assert all(wait_count == (1 if model.endswith(":free") else 0)
               for model, _, _, wait_count in calls)
    assert sum(stage == "secretary" for _, _, stage, _ in calls) == 2
    assert read_results(output)["question-0"]["used_secretary"]
    assert read_manifest(output)["execution"]["requests_per_minute"] == 18


def test_free_requests_waiting_for_rate_limit_leave_slots_for_paid_calls(monkeypatch):
    async def check():
        budget = RequestBudget(Schedule(request_concurrency=6, requests_per_minute=1))
        waiting = asyncio.Event()
        release = asyncio.Event()

        async def controlled_sleep(delay):
            if delay > 0:
                waiting.set()
                await release.wait()

        monkeypatch.setattr(asyncio, "sleep", controlled_sleep)

        async def request(paced):
            async with budget.acquire(paced=paced):
                return True

        assert await request(True)
        free = [asyncio.create_task(request(True)) for _ in range(6)]
        await waiting.wait()
        paid = asyncio.create_task(request(False))
        try:
            completed, _ = await asyncio.wait([paid], timeout=0.05)
            assert paid in completed, "rate-limited free requests occupied all HTTP slots"
        finally:
            release.set()
            await asyncio.gather(*free, paid)
        assert budget.started == 8

    asyncio.run(check())


@pytest.mark.parametrize("cancel_at", ["rate_wait", "slot_wait", "active"])
def test_cancelled_requests_release_capacity_without_spending_waiting_budget(cancel_at, monkeypatch):
    async def check():
        budget = RequestBudget(Schedule(request_concurrency=1, requests_per_minute=1,
                                        max_requests=3))
        sleeping = asyncio.Event()
        entered = asyncio.Event()
        hold = asyncio.Event()
        hold_rate = asyncio.Event()

        async def controlled_sleep(delay):
            sleeping.set()
            if cancel_at == "rate_wait" and delay > 0:
                await hold_rate.wait()

        monkeypatch.setattr(asyncio, "sleep", controlled_sleep)

        async def request(paced, wait=False):
            async with budget.acquire(paced=paced):
                entered.set()
                if wait:
                    await hold.wait()

        tasks = []
        if cancel_at == "rate_wait":
            await request(True)
            sleeping.clear()
        elif cancel_at == "slot_wait":
            holder = asyncio.create_task(request(False, wait=True))
            tasks.append(holder)
            await entered.wait()
        cancelled = asyncio.create_task(request(True, wait=cancel_at == "active"))
        tasks.append(cancelled)
        try:
            await sleeping.wait()
            if cancel_at == "active":
                await entered.wait()
            cancelled.cancel()
            with pytest.raises(asyncio.CancelledError):
                await cancelled
            assert budget.started == 1
        finally:
            hold.set()
            hold_rate.set()
            await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.wait_for(request(True), timeout=0.1)
        await asyncio.wait_for(request(False), timeout=0.1)
        assert budget.started == 3 and budget.exhausted

    asyncio.run(check())


@pytest.mark.parametrize("request_limit", [17, 18])
def test_all_models_secretaries_and_retries_share_six_slots_and_one_budget(request_limit):
    async def check():
        active = maximum = 0
        attempts = Counter()
        underlying_calls = []

        class Provider:
            name = "fixture"

            async def generate(self, request):
                nonlocal active, maximum
                active += 1
                maximum = max(maximum, active)
                underlying_calls.append(request)
                key = (request.task_id, request.agent_id)
                attempts[key] += 1
                try:
                    await asyncio.sleep(0.001)
                    if request.agent_id in "AG" and attempts[key] == 1:
                        return "malformed fixture response"
                    value = "1" if request.agent_id in "ABCG" else "2"
                    return json.dumps({"reasons": "fixture", "answer": value})
                finally:
                    active -= 1

        budget = RequestBudget(Schedule(request_concurrency=6, requests_per_minute=0,
                                        max_requests=request_limit))
        models = [ScheduledModel(Provider(), budget, paced_agents={"B", "E", "G"})
                  for _ in range(2)]
        results = await asyncio.gather(*(run_discussion(Task(str(i), "Question"), model,
            DiscussionConfig(rounds=1, max_attempts=2)) for i, model in enumerate(models)))
        assert maximum == 6
        assert active == 0
        assert budget.started == len(underlying_calls) == request_limit
        assert sum(r.used_secretary for r in results) == 2
        assert all(r.status == "completed" for r in results) == (request_limit == 18)
        assert sum(c.request.stage == "secretary" for r in results for c in r.calls) == 4
        with pytest.raises(ModelError, match="budget exhausted"):
            await models[0].generate(underlying_calls[0])
        assert len(underlying_calls) == request_limit

    asyncio.run(check())
