"""Final report tests use small saved ledgers, never credentials or live APIs."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location("evaluation_summary", Path(__file__).parents[1] / "scripts/summarize_evaluation.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


def save(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def opinion(answer):
    return {"answer": {"value": answer}}


def record(task_id, answer="A", status="completed", *, initial=("A", "A"), secretary=False, cost=0.1):
    return {"task_id": task_id, "question": task_id, "reference": "A", "answer_type": "choice", "metric": "exact",
            "category": "spatial", "status": status, "answer": answer, "used_secretary": secretary,
            "rounds": [[opinion(a) for a in initial], [opinion(answer)]] if initial else [],
            "calls": [{"request": {"stage": "secretary" if secretary else "discussion"},
                       "error": "Truncated model output" if status == "failed" else None,
                       "completion": {"model": "test/model", "provider": "Mock", "usage": {"cost": cost, "prompt_tokens": 10}}}]}


@pytest.fixture
def campaign(tmp_path, monkeypatch):
    monkeypatch.setattr(summary, "EXPECTED_QUESTIONS", dict.fromkeys(summary.DATASETS, 2))
    root = tmp_path / "campaign"
    root.mkdir()
    for dataset in summary.DATASETS:
        directory = root / dataset
        directory.mkdir()
        save(directory / "suite.json", {"task_ids": ["a", "b"], "experiments": list(summary.CONDITIONS), "synthetic": False})
        for name in summary.CONDITIONS:
            child = directory / name
            child.mkdir()
            model = {"model": "test/model", "reasoning": {"effort": "none"}, "max_completion_tokens": 64,
                     "provider": {"only": ["test"], "max_price": {"prompt": 1, "completion": 2}}}
            save(child / "manifest.json", {"task_ids": ["a", "b"], "synthetic": False,
                 "dataset_sha256": "data", "prompts_sha256": "prompts", "config_sha256": "config",
                 "config": {"model": model, "secretary_model": model, "discussion": {"agents": 6, "rounds": 3},
                            "agent_models": {"A": model, "B": dict(model, model="test/other")}}})
            records = [record("a"), record("b")]
            if name == "single-1":
                records = [record("a", "B", initial=("B",)), record("b", None, "failed", initial=())]
            elif name == "cmd-1":
                records = [record("a", initial=("B", "B")), record("b", initial=("A", "B"), secretary=True)]
            elif name == "single-3":
                records.insert(0, record("a", None, "failed", initial=(), cost=0.25))
                records[0]["calls"].append({"request": {"stage": "discussion"}, "error": "HTTP 503", "completion": None})
            (child / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
        save(directory / "reused_conditions.json", {
            "source": "/saved/pilot", "conditions": {"single-1": {"copied_tasks": 1, "copied_attempts": 1,
                "source": "/saved/pilot/single-1", "original_manifest": {"large": "omitted"}, "results_sha256": "old-hash"}}})
    return root


def test_final_report_counts_failed_latest_and_all_saved_attempt_costs(campaign, tmp_path):
    output = tmp_path / "report"
    result = summary.generate(campaign, output)
    totals = result["totals"]
    assert totals["dataset_questions"] == 6
    assert totals["planned_task_conditions"] == 42
    assert totals["completed"] == 39
    assert totals["failed"] == 3
    assert totals["pending"] == 0
    assert totals["calls"] == 48
    assert totals["usage"]["cost"] == pytest.approx(4.95)
    assert totals["calls_without_cost"] == 3
    assert totals["secretary_calls"] == 3
    mindcube = result["datasets"]["mindcube"]
    assert mindcube["experiments"]["single-1"]["accuracy"] == 0
    assert mindcube["experiments"]["single-3"]["accuracy"] == 1
    assert mindcube["paired"]["cmd-1 vs single-1"]["improved"] == 1
    assert mindcube["paired"]["cmd-1 vs single-1"]["excluded_failed_or_pending"] == 1
    changes = mindcube["experiments"]["cmd-1"]["discussion_changes"]
    assert changes["wrong_to_correct"] == 1
    assert changes["initial_ties"] == 1
    assert changes["final_correct_after_initial_tie"] == 1
    assert "original_manifest" not in mindcube["evidence"]["reuse"]["conditions"]["single-1"]
    assert mindcube["evidence"]["conditions"]["cmd-1"]["results_sha256"] == summary.sha256(campaign / "mindcube/cmd-1/results.jsonl")
    assert mindcube["experiments"]["single-3"]["call_errors"] == {"HTTP 503": 1, "Truncated model output": 1}
    with (output / "mindcube.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[1]["cmd-1.initial_vote"] == "TIE"
    assert rows[1]["single-1.status"] == "failed"
    assert rows[1]["single-1.answer"] == ""
    assert rows[1]["single-1.initial_vote"] == "UNAVAILABLE"
    rendered = (output / "report.md").read_text()
    assert "39 completed, 3 failed, 0 pending" in rendered
    assert "including any final secretary call" in rendered
    assert "test/other" in rendered
    assert "routing ceilings" in rendered
    assert "unsaved in-flight calls" in rendered


def test_pending_task_prevents_any_final_output_even_in_last_dataset(campaign, tmp_path):
    path = campaign / "aime2026/cmd-mixed/results.jsonl"
    path.write_text(json.dumps(record("a")) + "\n")
    output = tmp_path / "report"
    with pytest.raises(ValueError, match="pending tasks"):
        summary.generate(campaign, output)
    assert not output.exists()


def test_calibration_adds_only_histories_not_already_in_evaluation(campaign, tmp_path):
    archive = tmp_path / "calibration"
    for condition in ("single-1", "single-2", "single-3"):
        child = archive / condition
        child.mkdir(parents=True)
        if condition == "single-2":
            extra = [record("a", cost=0.7), record("b", status="failed")]
            extra[1]["calls"][0]["completion"] = None
            content = "".join(json.dumps(r) + "\n" for r in extra)
        else:
            # Includes an older failed attempt followed by a successful attempt.
            content = (campaign / "aime2025" / condition / "results.jsonl").read_text()
        (child / "results.jsonl").write_text(content)
    save(campaign / "calibration.json", {"aime2025": {"archive": str(archive), "experiments": {
        condition: {"usage": {"cost": 999}} for condition in ("single-1", "single-2", "single-3")}}})
    output = tmp_path / "report"
    result = summary.generate(campaign, output)
    calibration = result["calibration"]
    assert calibration["additional_calls"] == 2
    assert calibration["additional_recorded_cost"] == pytest.approx(0.7)
    assert calibration["calls_without_cost"] == 1
    assert sum(c["already_counted_calls"] for c in calibration["conditions"]) == 6
    assert result["totals"]["usage"]["cost"] == pytest.approx(4.95)
    assert result["totals"]["recorded_cost_including_calibration"] == pytest.approx(5.65)
    assert "**$0.700000**" in (output / "report.md").read_text()
    assert "**$5.650000**" in (output / "report.md").read_text()


def test_public_paths_preserve_raw_evidence_hashes_and_accounting(campaign, tmp_path, monkeypatch):
    external = str(tmp_path.parent / "external/tasks.jsonl")
    for dataset in summary.DATASETS:
        tasks = tmp_path / "data" / dataset / "tasks.jsonl"
        tasks.parent.mkdir(parents=True)
        tasks.write_text("{}\n")
        save(tasks.parent / "provenance.json", {
            "tasks_sha256": "data", "source_files": [{"path": str(tasks), "sha256": "source-hash"}],
            "external_source": external, "source_url": "https://example.org/data",
            "path_labels": {str(tasks): "original key"},
        })
        for condition in summary.CONDITIONS:
            path = campaign / dataset / condition / "manifest.json"
            manifest = summary.read_json(path)
            save(path, dict(manifest, source=str(tasks)))
        path = campaign / dataset / "reused_conditions.json"
        reuse = summary.read_json(path)
        reuse["source"] = str(tmp_path / "pilot")
        reuse["conditions"]["single-1"]["source"] = str(tmp_path / "pilot/single-1")
        save(path, reuse)
    archive = tmp_path / "calibration/single-2"
    archive.mkdir(parents=True)
    (archive / "results.jsonl").write_text(json.dumps(record("a", cost=0.7)) + "\n")
    save(campaign / "calibration.json", {
        "aime2025": {"archive": str(archive.parent), "experiments": {"single-2": {}}},
    })
    raw = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    baseline_output = tmp_path / "baseline"
    expected = summary.generate(campaign, baseline_output)

    monkeypatch.setattr(summary, "REPOSITORY_ROOT", tmp_path)
    output = tmp_path / "public"
    result = summary.generate(campaign, output)
    # The complete summary must differ only in its timestamp and these path values.
    expected["generated_at"] = result["generated_at"]
    for dataset in summary.DATASETS:
        evidence = expected["datasets"][dataset]["evidence"]
        evidence["source_directory"] = f"campaign/{dataset}"
        evidence["dataset_source"] = f"data/{dataset}/tasks.jsonl"
        evidence["provenance"]["source_files"][0]["path"] = f"data/{dataset}/tasks.jsonl"
        evidence["reuse"]["source"] = "pilot"
        evidence["reuse"]["conditions"]["single-1"]["source"] = "pilot/single-1"
        assert evidence["provenance"]["external_source"] == external
        assert result["datasets"][dataset]["evidence"]["provenance"]["provenance_file_sha256"] == summary.sha256(
            tmp_path / "data" / dataset / "provenance.json"
        )
        assert (output / f"{dataset}.csv").read_bytes() == (baseline_output / f"{dataset}.csv").read_bytes()
    expected["calibration"]["conditions"][0]["source"] = "calibration/single-2/results.jsonl"
    assert result == expected
    assert summary.read_json(output / "evaluation.json") == expected
    assert all(path.read_bytes() == content for path, content in raw.items())
    rendered = (output / "report.md").read_text()
    assert "Reused histories from `pilot`" in rendered
    assert "relative to the repository root" in rendered
    assert "recorded hashes refer to those original files" in rendered


def test_pilot_cannot_be_published_as_full_dataset(campaign, tmp_path, monkeypatch):
    monkeypatch.setattr(summary, "EXPECTED_QUESTIONS", {"mindcube": 1050, "aime2025": 30, "aime2026": 30})
    output = tmp_path / "report"
    with pytest.raises(ValueError, match="Full mindcube requires 1050 tasks, found 2"):
        summary.generate(campaign, output)
    assert not output.exists()


def test_invalid_expressions_remain_failed_and_errors_are_grouped_only_in_markdown(campaign, tmp_path):
    path = campaign / "aime2026/single-1/results.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    expression_error = "ValueError: invalid numeric answer: '41 + sqrt(85)'"
    records[1]["calls"][0]["error"] = expression_error
    path.write_text("".join(json.dumps(r) + "\n" for r in records))
    output = tmp_path / "report"
    result = summary.generate(campaign, output)
    report = result["datasets"]["aime2026"]["experiments"]["single-1"]
    assert report["call_errors"] == {expression_error: 1}
    assert report["call_error_types"] == {"Invalid numeric answer": 1}
    assert report["failed"] == 1
    assert report["correct"] == 0
    assert "Invalid numeric answer: 1" in (output / "report.md").read_text()
    assert "sqrt(85)" not in (output / "report.md").read_text()


@pytest.mark.parametrize("mutation", ["synthetic", "missing_condition", "duplicate_ids", "nonterminal"])
def test_invalid_campaign_is_not_published(campaign, tmp_path, mutation):
    suite_path = campaign / "mindcube/suite.json"
    suite = json.loads(suite_path.read_text())
    if mutation == "synthetic":
        suite["synthetic"] = True
    elif mutation == "missing_condition":
        suite["experiments"].pop()
    elif mutation == "duplicate_ids":
        suite["task_ids"].append("a")
    else:
        path = campaign / "mindcube/single-1/results.jsonl"
        path.write_text(json.dumps(record("a", status="pending")) + "\n" + json.dumps(record("b")) + "\n")
    save(suite_path, suite)
    output = tmp_path / "report"
    with pytest.raises(ValueError):
        summary.generate(campaign, output)
    assert not output.exists()


def test_running_campaign_is_not_published(campaign, tmp_path):
    save(campaign / "campaign-status.json", {"state": "running"})
    with pytest.raises(ValueError, match="campaign is running"):
        summary.generate(campaign, tmp_path / "report")


def test_ledger_change_during_read_is_not_published(campaign, tmp_path, monkeypatch):
    original = summary.evaluate_suite

    def mutate(directory):
        result = original(directory)
        with (directory / "single-1/results.jsonl").open("a") as handle:
            handle.write(json.dumps(record("a")) + "\n")
        return result

    monkeypatch.setattr(summary, "evaluate_suite", mutate)
    with pytest.raises(ValueError, match="Inputs changed while reading"):
        summary.generate(campaign, tmp_path / "report")


def test_cli_errors_without_touching_existing_report(campaign, tmp_path, capsys):
    output = tmp_path / "report"
    output.mkdir()
    (output / "report.md").write_text("existing")
    (campaign / "aime2026/cmd-2/results.jsonl").write_text("")
    assert summary.main(["--input", str(campaign), "--output", str(output)]) == 2
    assert (output / "report.md").read_text() == "existing"
    assert "pending tasks" in capsys.readouterr().err


def test_later_dataset_cannot_hide_change_to_an_already_read_ledger(campaign, tmp_path, monkeypatch):
    original = summary.summarize_dataset

    def mutate(directory):
        result = original(directory)
        if directory.name == "aime2026":
            with (campaign / "mindcube/single-1/results.jsonl").open("a") as handle:
                handle.write(json.dumps(record("a")) + "\n")
        return result

    monkeypatch.setattr(summary, "summarize_dataset", mutate)
    output = tmp_path / "report"
    with pytest.raises(ValueError, match="Campaign inputs changed"):
        summary.generate(campaign, output)
    assert not output.exists()
