"""Run a subset now, then resume the same planned comparison offline."""

import json

import pytest

from llm_discussion import cli
from llm_discussion.storage import read_manifest, read_results


CONDITIONS = {"single-1", "single-2", "single-3", "cmd-1", "cmd-2", "cmd-3", "cmd-mixed"}


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("condition-selection checks must not read credentials or contact a provider")

    monkeypatch.setattr(cli, "load_dotenv", forbidden)
    monkeypatch.setattr(cli, "OpenRouterModel", forbidden)


@pytest.fixture
def suite_args(tmp_path):
    config = tmp_path / "suite-config.json"
    config.write_text(json.dumps({
        "discussion": {"agents": 6, "group_size": 3, "rounds": 3},
        "models": [{"model": f"fixture/model-{i}"} for i in range(3)],
    }))
    data = tmp_path / "tasks.jsonl"
    data.write_text("\n".join(json.dumps({
        "id": f"task-{i}", "question": f"Question {i}", "reference": "A",
        "answer_type": "choice", "options": ["cube", "sphere"],
    }) for i in range(2)) + "\n")
    output = tmp_path / "suite"
    return (["suite", "--config", str(config), "--dataset", str(data), "--dry-run",
             "--limit", "2", "--output", str(output)], output)


def test_selected_conditions_preserve_the_full_plan_and_resume_the_remainder(suite_args, capsys):
    args, output = suite_args
    selected = {"single-1", "cmd-mixed"}
    # A selected subset deliberately leaves the overall comparison incomplete.
    assert cli.main(args + ["--conditions", *sorted(selected)]) == 1
    summary = json.loads(capsys.readouterr().out)
    assert summary["written"] == 4
    assert summary["unfinished"] == 10
    assert summary["requests_started"] == 2 * (1 + 6 * 3)
    suite_before = (output / "suite.json").read_bytes()
    suite = json.loads(suite_before)
    assert set(suite["experiments"]) == CONDITIONS
    assert suite["task_ids"] == ["task-0", "task-1"]
    selected_results = {}
    for name in CONDITIONS:
        assert read_manifest(output / name)["task_ids"] == suite["task_ids"]
        records = read_results(output / name)
        assert set(records) == (set(suite["task_ids"]) if name in selected else set())
        if name in selected:
            selected_results[name] = (output / name / "results.jsonl").read_bytes()

    assert cli.main(args + ["--resume"]) == 0
    resumed = json.loads(capsys.readouterr().out)
    assert resumed["written"] == 10
    assert resumed["skipped_completed"] == 4
    assert resumed["unfinished"] == 0
    assert resumed["requests_started"] == 2 * (2 + 3 * 6 * 3)
    assert (output / "suite.json").read_bytes() == suite_before
    for name in CONDITIONS:
        assert set(read_results(output / name)) == set(suite["task_ids"])
        if name in selected:
            assert (output / name / "results.jsonl").read_bytes() == selected_results[name]


@pytest.mark.parametrize("selected", [["unknown"], ["single-1", "unknown"]])
def test_invalid_condition_creates_no_output(suite_args, selected, capsys):
    args, output = suite_args
    assert cli.main(args + ["--conditions", *selected]) == 2
    captured = capsys.readouterr()
    assert "Unknown conditions: unknown" in captured.err
    assert captured.out == ""
    assert not output.exists()
