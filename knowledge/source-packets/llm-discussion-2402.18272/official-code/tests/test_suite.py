import asyncio
from collections import defaultdict
import json
import shutil

import pytest

from llm_discussion import cli
from llm_discussion.config import load_suite
from llm_discussion.engine import run_discussion
from llm_discussion.models import DryRunModel
from llm_discussion.reporting import evaluate_suite
from llm_discussion.scheduling import RequestBudget, Schedule, ScheduledModel, run_jobs
from llm_discussion.storage import read_manifest, read_results
from llm_discussion.types import DiscussionConfig, Task


@pytest.fixture
def suite_files(tmp_path):
    config = tmp_path / "suite.json"
    config.write_text(json.dumps({
        "discussion": {"agents": 6, "group_size": 3, "rounds": 3, "max_attempts": 2},
        "models": [{"model": f"vendor/model-{i}"} for i in range(3)], "secretary": 1,
    }))
    data = tmp_path / "tasks.jsonl"
    data.write_text("\n".join(json.dumps({
        "id": f"q-{i}", "question": f"Unique question {i}?", "reference": "C",
        "answer_type": "choice", "options": ["one", "two", "three"],
        "category": ("among", "around", "rotation")[i % 3],
    }) for i in range(9)))
    return config, data


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("suite dry run touched credentials or a real provider")

    monkeypatch.setattr(cli, "load_dotenv", forbidden)
    monkeypatch.setattr(cli, "OpenRouterModel", forbidden)


def suite_args(suite_files, output):
    config, data = suite_files
    return ["suite", "--config", str(config), "--dataset", str(data), "--dry-run",
            "--scenario", "tie", "--limit", "3", "--sample-seed", "42", "--output", str(output)]


def test_suite_has_seven_balanced_conditions(suite_files):
    configs = load_suite(suite_files[0])
    assert set(configs) == {"single-1", "single-2", "single-3", "cmd-1", "cmd-2", "cmd-3", "cmd-mixed"}
    for i in range(1, 4):
        assert configs[f"single-{i}"].discussion.agents == configs[f"single-{i}"].discussion.rounds == 1
        assert configs[f"single-{i}"].model == configs[f"cmd-{i}"].model
        assert not configs[f"cmd-{i}"].agent_models
    mixed = configs["cmd-mixed"]
    for group in ("ABC", "DEF"):
        assert {mixed.agent_models[agent].model for agent in group} == {f"vendor/model-{i}" for i in range(3)}
    assert mixed.secretary_model.model == "vendor/model-1"


def test_suite_uses_matched_samples_and_never_scores_synthetic(suite_files, tmp_path, capsys):
    output = tmp_path / "run"
    assert cli.main(suite_args(suite_files, output)) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["written"] == 21
    assert summary["requests_started"] == 237
    suite = json.loads((output / "suite.json").read_text())
    assert len(suite["task_ids"]) == 3
    for name in suite["experiments"]:
        assert read_manifest(output / name)["task_ids"] == suite["task_ids"]
        records = read_results(output / name)
        assert set(records) == set(suite["task_ids"])
        assert {r["category"] for r in records.values()} == {"among", "around", "rotation"}
        assert all(len(r["calls"]) == (1 if name.startswith("single") else 19) for r in records.values())
    report = evaluate_suite(output)
    assert report["paired"] == {}
    assert all(r["accuracy"] is None and "correct" not in r for r in report["experiments"].values())


def test_multitask_suite_shares_request_limit_and_keeps_round_barriers(suite_files, tmp_path, monkeypatch):
    active = maximum = 0
    finished = defaultdict(set)
    instances = []

    class TrackingModel(DryRunModel):
        def __init__(self, *args):
            super().__init__(*args)
            self.identity = len(instances)
            instances.append(self)

        async def generate(self, request):
            nonlocal active, maximum
            if request.stage == "discussion" and request.round > 1:
                assert len(finished[self.identity, request.task_id, request.round - 1]) == self.agents
            active += 1
            maximum = max(maximum, active)
            try:
                await asyncio.sleep(0.0001)
                answer = json.loads(await super().generate(request))
                answer["reasons"] = f"private-{request.task_id}-{request.agent_id}-round-{request.round}"
                return json.dumps(answer)
            finally:
                active -= 1
                finished[self.identity, request.task_id, request.round].add(request.agent_id)

    monkeypatch.setattr(cli, "DryRunModel", TrackingModel)
    output = tmp_path / "run"
    assert cli.main(suite_args(suite_files, output) + ["--task-concurrency", "4", "--request-concurrency", "2"]) == 0
    assert maximum == 2
    for name in ("cmd-1", "cmd-2", "cmd-3", "cmd-mixed"):
        for record in read_results(output / name).values():
            for call in record["calls"]:
                request = call["request"]
                if request["stage"] != "discussion" or request["round"] == 1:
                    continue
                peers = request["messages"][3]["content"]
                own_group = "ABC" if request["agent_id"] in "ABC" else "DEF"
                for agent in "ABCDEF":
                    expected = agent in own_group and agent != request["agent_id"]
                    assert (f'private-{record["task_id"]}-{agent}-round-{request["round"] - 1}' in peers) == expected


def test_shared_budget_counts_parse_retries_across_tasks():
    async def check():
        seen = set()

        class OnceMalformed:
            name = "retry-test"

            async def generate(self, request):
                key = (request.task_id, request.agent_id)
                if request.agent_id == "A" and key not in seen:
                    seen.add(key)
                    return "invalid answer"
                return '{"reasons":"fixture", "answer":"1"}'

        budget = RequestBudget(Schedule(request_concurrency=2, requests_per_minute=0, max_requests=9))
        model = ScheduledModel(OnceMalformed(), budget)
        results = []

        async def work(index):
            results.append(await run_discussion(Task(str(index), "q"), model,
                DiscussionConfig(agents=2, group_size=1, rounds=1, max_attempts=2)))

        await run_jobs(range(3), work, 3)
        assert budget.started == 9
        assert all(r.status == "completed" and r.votes == {"1": 2} for r in results)
        assert sum(len(r.calls) for r in results) == 9

    asyncio.run(check())


def test_resume_skips_completed_and_restores_missing_condition(suite_files, tmp_path, capsys):
    output = tmp_path / "run"
    args = suite_args(suite_files, output)
    assert cli.main(args) == 0
    before = (output / "cmd-1" / "results.jsonl").read_bytes()
    shutil.rmtree(output / "single-3")
    capsys.readouterr()
    assert cli.main(args + ["--resume"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["written"] == summary["requests_started"] == 3
    assert summary["skipped_completed"] == 18
    assert (output / "cmd-1" / "results.jsonl").read_bytes() == before


def test_resume_requires_existing_output_and_never_overwrites(suite_files, tmp_path):
    output = tmp_path / "run"
    args = suite_args(suite_files, output)
    assert cli.main(args + ["--resume"]) == 2
    assert not output.exists()
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("keep")
    assert cli.main(args) == 2
    assert marker.read_text() == "keep"


def test_exact_request_budget_can_finish_successfully(tmp_path):
    output = tmp_path / "run"
    assert cli.main(["run", "--dry-run", "--agents", "1", "--group-size", "1", "--rounds", "1",
                     "--max-requests", "1", "--output", str(output)]) == 0
    assert read_results(output)["question-0"]["status"] == "completed"


def test_suite_budget_leaves_pending_tasks_and_resume_finishes_them(suite_files, tmp_path, capsys):
    output = tmp_path / "run"
    args = suite_args(suite_files, output)
    assert cli.main(args + ["--max-requests", "1"]) == 1
    summary = json.loads(capsys.readouterr().out)
    assert summary["requests_started"] == 1
    report = evaluate_suite(output)
    assert sum(r["pending"] for r in report["experiments"].values()) > 0
    assert all(r["accuracy"] is None for r in report["experiments"].values())
    completed = (output / "single-1" / "results.jsonl").read_bytes()
    first_task = json.loads(completed.splitlines()[0])["task_id"]
    assert cli.main(args + ["--resume", "--max-requests", "300"]) == 0
    resumed = (output / "single-1" / "results.jsonl").read_bytes()
    assert resumed.startswith(completed)
    assert sum(json.loads(line)["task_id"] == first_task for line in resumed.splitlines()) == 1
    report = evaluate_suite(output)
    assert all(r["pending"] == r["failed"] == 0 for r in report["experiments"].values())


def test_paired_reporting_excludes_failed_or_pending_service_results(tmp_path):
    ids = ["a", "b", "c", "d"]
    (tmp_path / "suite.json").write_text(json.dumps({
        "experiments": ["single-1", "cmd-mixed"], "task_ids": ids, "synthetic": False,
    }))

    def record(task_id, answer, status="completed"):
        return {"task_id": task_id, "answer": answer, "status": status, "reference": "A", "answer_type": "choice"}

    for name, records in {
        "single-1": [record("a", "B"), record("b", "A"), record("c", None, "failed")],
        "cmd-mixed": [record("a", "A"), record("b", "B"), record("c", "A"), record("d", "A")],
    }.items():
        directory = tmp_path / name
        directory.mkdir()
        (directory / "manifest.json").write_text(json.dumps({
            "task_ids": ids, "synthetic": False, "dataset_sha256": "same-dataset",
            "prompts_sha256": "same-prompts", "config": {"model": {"model": f"vendor/{name}"}},
        }))
        (directory / "results.jsonl").write_text("\n".join(json.dumps(r) for r in records))
    result = evaluate_suite(tmp_path)
    assert result["experiments"]["single-1"]["accuracy"] is None
    assert result["experiments"]["cmd-mixed"]["accuracy"] == .75
    assert result["paired"]["cmd-mixed vs single-1"] == {
        "both_completed": 2, "improved": 1, "regressed": 1,
        "unchanged": 0, "excluded_failed_or_pending": 2, "excluded_unlabeled": 0,
    }
