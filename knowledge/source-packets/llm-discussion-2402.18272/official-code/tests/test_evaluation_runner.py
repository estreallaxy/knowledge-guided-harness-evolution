"""Campaign orchestration tests use fake subprocesses and never read credentials."""

import asyncio
from copy import deepcopy
import fcntl
import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location("evaluation_runner", Path(__file__).parents[1] / "scripts/run_evaluation.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


@pytest.fixture
def plan(monkeypatch):
    monkeypatch.setattr(runner, "load_suite", lambda _: {"single-1": None, "cmd-1": None})
    monkeypatch.setattr(runner, "load_tasks", lambda _: [None, None])
    monkeypatch.setattr(runner, "expected_manifests", lambda plan, dataset: {
        name: {"task_ids": ["a", "b"], "config_sha256": dataset.get("config", plan["config"]),
               "dataset_sha256": "data-sha", "prompts_sha256": "prompt-sha", "image_sha256": {"a.png": "image-sha"}}
        for name in ("single-1", "cmd-1")})
    return {"config": "example.json", "sample_seed": 42, "requests_per_minute": 0,
            "datasets": [{"name": "math", "path": "tasks.jsonl", "limit": 2,
                          "task_concurrency": 2, "request_concurrency": 4,
                          "request_budget": 20, "max_passes": 2}]}


def finish(directory, config="example.json"):
    directory.mkdir(parents=True, exist_ok=True)
    suite = {"experiments": ["single-1", "cmd-1"], "task_ids": ["a", "b"], "synthetic": False}
    (directory / "suite.json").write_text(json.dumps(suite))
    for name in suite["experiments"]:
        child = directory / name
        child.mkdir(exist_ok=True)
        (child / "manifest.json").write_text(json.dumps({"task_ids": ["a", "b"], "config_sha256": config,
            "dataset_sha256": "data-sha", "prompts_sha256": "prompt-sha", "image_sha256": {"a.png": "image-sha"}}))
        (child / "results.jsonl").write_text("".join(json.dumps({"task_id": task, "status": "completed"}) + "\n" for task in ("a", "b")))


def spent(directory, count):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "executions.jsonl").open("a") as handle:
        handle.write(json.dumps({"requests_started": count}) + "\n")


class FakeProcess:
    pid = 1234
    returncode = None

    def __init__(self, callback):
        self.callback = callback

    async def wait(self):
        await asyncio.sleep(0)
        self.returncode = self.callback()
        return self.returncode


def test_parallel_workers_resume_and_cumulative_retry_budget(plan, tmp_path, monkeypatch):
    plan["datasets"].append(dict(plan["datasets"][0], name="spatial"))
    spent(tmp_path / "math", 3)  # Existing baseline is part of the total budget.
    commands, calls = [], {}

    async def spawn(*command, **kwargs):
        commands.append(command)
        directory = Path(command[command.index("--output") + 1])
        name = directory.name
        calls[name] = calls.get(name, 0) + 1
        number = calls[name]

        def done():
            assert len(commands) >= 2  # Both datasets launch before either finishes.
            spent(directory, 4)
            if number == 2:
                finish(directory)
            return 1 if number == 1 else 0

        return FakeProcess(done)

    monkeypatch.setattr(runner.asyncio, "create_subprocess_exec", spawn)
    assert asyncio.run(runner.run_campaign(plan, tmp_path)) == 0
    math = [c for c in commands if Path(c[c.index("--output") + 1]).name == "math"]
    assert [int(c[c.index("--max-requests") + 1]) for c in math] == [17, 13]
    assert all("--resume" in c for c in math)
    spatial = [c for c in commands if Path(c[c.index("--output") + 1]).name == "spatial"]
    assert "--resume" not in spatial[0] and "--resume" in spatial[1]
    status = json.loads((tmp_path / "campaign-status.json").read_text())
    assert status["state"] == "completed"
    assert status["datasets"]["math"]["requests_consumed"] == 11


def test_completed_suite_skips_calls(plan, tmp_path, monkeypatch):
    finish(tmp_path / "math")
    monkeypatch.setattr(runner.asyncio, "create_subprocess_exec", lambda *a, **kw: pytest.fail("unexpected call"))
    assert asyncio.run(runner.run_campaign(plan, tmp_path)) == 0


def test_dataset_config_override_is_validated_and_used(plan, tmp_path, monkeypatch):
    plan["datasets"][0]["config"] = "math-config.json"
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))
    loaded = []
    monkeypatch.setattr(runner, "load_suite", lambda path: loaded.append(str(path)))
    assert runner.load_plan(path) == plan
    assert loaded == ["example.json", "math-config.json"]

    async def spawn(*command, **kwargs):
        assert command[command.index("--config") + 1] == "math-config.json"
        return FakeProcess(lambda: (spent(tmp_path / "math", 4), finish(tmp_path / "math", "math-config.json"), 0)[2])

    monkeypatch.setattr(runner.asyncio, "create_subprocess_exec", spawn)
    assert asyncio.run(runner.run_campaign(plan, tmp_path)) == 0


@pytest.mark.parametrize("field,value", [
    ("config_sha256", "different-config"), ("dataset_sha256", "different-data"),
    ("prompts_sha256", "different-prompts"), ("image_sha256", {"a.png": "different-image"}),
])
def test_completed_suite_with_changed_inputs_is_rejected(plan, tmp_path, monkeypatch, field, value):
    finish(tmp_path / "math")
    path = tmp_path / "math" / "cmd-1" / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest[field] = value
    path.write_text(json.dumps(manifest))
    monkeypatch.setattr(runner.asyncio, "create_subprocess_exec", lambda *a, **kw: pytest.fail("unexpected call"))
    assert asyncio.run(runner.run_campaign(plan, tmp_path)) == 1
    state = json.loads((tmp_path / "campaign-status.json").read_text())
    assert state["datasets"]["math"]["state"] == "error"
    assert field in state["datasets"]["math"]["error"]


@pytest.mark.parametrize("returncode", [1, 2])
def test_maximum_passes_persist_across_restarts(plan, tmp_path, monkeypatch, returncode):
    calls = []

    async def spawn(*command, **kwargs):
        calls.append(command)
        directory = Path(command[command.index("--output") + 1])
        return FakeProcess(lambda: (spent(directory, 2), returncode)[1])

    monkeypatch.setattr(runner.asyncio, "create_subprocess_exec", spawn)
    assert asyncio.run(runner.run_campaign(plan, tmp_path)) == 1
    assert len(calls) == (2 if returncode == 1 else 1)
    if returncode == 1:
        assert asyncio.run(runner.run_campaign(plan, tmp_path)) == 1
        assert len(calls) == 2


def test_existing_budget_exhaustion_prevents_calls(plan, tmp_path, monkeypatch):
    spent(tmp_path / "math", 20)
    monkeypatch.setattr(runner.asyncio, "create_subprocess_exec", lambda *a, **kw: pytest.fail("unexpected call"))
    assert asyncio.run(runner.run_campaign(plan, tmp_path)) == 1
    status = json.loads((tmp_path / "campaign-status.json").read_text())
    assert status["datasets"]["math"]["state"] == "budget_exhausted"


@pytest.mark.parametrize("mutation", [
    lambda p: p["datasets"][0].update(name="../outside"),
    lambda p: p["datasets"][0].update(request_budget=0),
    lambda p: p["datasets"][0].update(max_passes=3),
    lambda p: p["datasets"][0].update(limit=3),
    lambda p: p.update(requests_per_minute=float("inf")),
    lambda p: p["datasets"].append(deepcopy(p["datasets"][0])),
])
def test_invalid_plan_rejected_before_subprocess(plan, tmp_path, mutation):
    mutation(plan)
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))
    with pytest.raises(ValueError):
        runner.load_plan(path)


def test_changed_plan_cannot_resume(plan, tmp_path):
    finish(tmp_path / "math")
    asyncio.run(runner.run_campaign(plan, tmp_path))
    plan["datasets"][0]["request_budget"] += 1
    with pytest.raises(ValueError, match="changed plan"):
        asyncio.run(runner.run_campaign(plan, tmp_path))


def test_lock_prevents_overlapping_drivers(plan, tmp_path):
    with (tmp_path / ".campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match="holds the lock"):
            asyncio.run(runner.run_campaign(plan, tmp_path))


def test_cancellation_terminates_child_and_preserves_allocation(plan, tmp_path, monkeypatch):
    async def scenario():
        launched, exited = asyncio.Event(), asyncio.Event()

        class Process:
            pid = 123
            returncode = None

            async def wait(self):
                await exited.wait()
                return self.returncode

            def terminate(self):
                self.returncode = -15
                exited.set()

        async def spawn(*args, **kwargs):
            launched.set()
            return Process()

        monkeypatch.setattr(runner.asyncio, "create_subprocess_exec", spawn)
        task = asyncio.create_task(runner.run_campaign(plan, tmp_path))
        await launched.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert exited.is_set()

    asyncio.run(scenario())
    status = json.loads((tmp_path / "campaign-status.json").read_text())
    assert status["state"] == "interrupted"
    assert status["datasets"]["math"]["requests_consumed"] == 20
    monkeypatch.setattr(runner.asyncio, "create_subprocess_exec", lambda *a, **kw: pytest.fail("unexpected call"))
    assert asyncio.run(runner.run_campaign(plan, tmp_path)) == 1
