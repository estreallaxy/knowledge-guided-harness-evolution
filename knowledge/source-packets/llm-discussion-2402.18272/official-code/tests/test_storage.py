import json

import pytest

from llm_discussion.storage import evaluate, prepare_run, score_answer


def save_run(directory, records, *, synthetic=False, ids=("a", "b")):
    (directory / "manifest.json").write_text(json.dumps({"synthetic": synthetic, "task_ids": list(ids)}))
    (directory / "results.jsonl").write_text("\n".join(json.dumps(r) for r in records))


def test_evaluation_includes_failed_tasks_and_latest_attempt(tmp_path):
    save_run(tmp_path, [
        {"task_id": "a", "status": "completed", "reference": "-1", "answer": "1"},
        {"task_id": "a", "status": "completed", "reference": "-1", "answer": "-1.00"},
        {"task_id": "b", "status": "failed", "reference": "2", "answer": None},
    ])
    result = evaluate(tmp_path)
    assert result["accuracy"] == 0.5
    assert result["failed"] == 1
    assert result["tasks"] == 2


def test_pending_tasks_hide_accuracy(tmp_path):
    save_run(tmp_path, [{"task_id": "a", "status": "completed", "reference": "1", "answer": "1"}])
    result = evaluate(tmp_path)
    assert result["pending"] == 1
    assert result["accuracy"] is None


def test_synthetic_tasks_never_report_accuracy(tmp_path):
    save_run(tmp_path, [{"task_id": "a", "status": "completed", "reference": "1", "answer": "1"}],
             synthetic=True, ids=("a",))
    assert evaluate(tmp_path)["accuracy"] is None


def test_resume_rejects_partial_json_without_touching_data(tmp_path):
    manifest = {"synthetic": True, "task_ids": ["a"]}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    partial = '{"task_id":'
    (tmp_path / "results.jsonl").write_text(partial)
    with pytest.raises(ValueError, match="line 1"):
        prepare_run(tmp_path, manifest, resume=True)
    assert (tmp_path / "results.jsonl").read_text() == partial


def test_choice_failures_count_but_old_attempt_costs_are_retained(tmp_path):
    def call(cost, error=None):
        return {"error": error, "completion": {"usage": {"cost": cost, "prompt_tokens": 10}}}

    save_run(tmp_path, [
        {"task_id": "a", "status": "failed", "reference": "A", "answer": None,
         "answer_type": "choice", "category": "direction", "calls": [call(.1, "parse error")]},
        {"task_id": "a", "status": "completed", "reference": "A", "answer": "a",
         "answer_type": "choice", "category": "direction", "calls": [call(.2)]},
        {"task_id": "b", "status": "failed", "reference": "B", "answer": None,
         "answer_type": "choice", "category": "distance", "calls": [call(.3, "parse error")]},
    ])
    result = evaluate(tmp_path)
    assert result["accuracy"] == 0.5
    assert result["categories"]["direction"]["mean_score"] == 1
    assert result["categories"]["distance"]["mean_score"] == 0
    assert result["task_attempts"] == 3
    assert result["calls"] == 3
    assert result["failed_calls"] == 2
    assert result["usage"]["cost"] == pytest.approx(.6)
    assert result["usage"]["prompt_tokens"] == 30


@pytest.mark.parametrize("reference,predicted,expected", [
    ("100", "100", 1), ("100", "110", .9), ("100", "151", 0),
    ("0", "0", 1), ("0", "1", 0),
])
def test_mra_relative_thresholds(reference, predicted, expected):
    assert score_answer({"reference": reference, "metric": "mra"}, predicted) == expected


def test_exact_accuracy_and_mra_denominators_stay_separate(tmp_path):
    save_run(tmp_path, [
        {"task_id": "a", "status": "completed", "reference": "A", "answer": "A", "answer_type": "choice"},
        {"task_id": "b", "status": "failed", "reference": "100", "answer": None, "metric": "mra"},
    ])
    result = evaluate(tmp_path)
    assert result["accuracy"] == 1
    assert result["exact_tasks"] == 1
    assert result["mra"] == 0


def test_discussion_changes_separate_initial_ties_and_exclude_failed_or_unscored_tasks(tmp_path):
    def record(task_id, initial, answer, **fields):
        return {"task_id": task_id, "status": "completed", "reference": "A", "answer": answer,
                "answer_type": "choice", "rounds": [[{"answer": {"value": value}} for value in initial], []],
                **fields}

    records = [
        record("improved", "BBBAAAAB", "A"),  # Tied votes are not improvements.
        record("wrong-right", "BBBAA", "A"),
        record("right-wrong", "AAB", "B"),
        record("right-right", "AAB", "A"),
        record("wrong-wrong", "BBA", "B"),
        record("tied-wrong", "AB", "B"),
        record("failed", "AAA", None, status="failed"),
        record("unlabeled", "AAA", "A", reference=None),
        record("mra", "100", "100", reference="100", answer_type="number", metric="mra"),
        record("single", "A", "A", rounds=[[{"answer": {"value": "A"}}]]),
    ]
    save_run(tmp_path, records, ids=[r["task_id"] for r in records] + ["pending"])
    report = evaluate(tmp_path)
    assert report["accuracy"] is None
    changes = report["discussion_changes"]
    assert changes["completed_exact_tasks"] == 6
    assert changes["compared_unique_votes"] == 4
    assert all(changes[key] == 1 for key in (
        "wrong_to_correct", "correct_to_wrong", "correct_to_correct", "wrong_to_wrong"))
    assert changes["initial_ties"] == 2
    assert changes["final_correct_after_initial_tie"] == 1


def test_initial_vote_accuracy_excludes_failed_discussions(tmp_path):
    save_run(tmp_path, [
        {"task_id": "a", "status": "completed", "reference": "1", "answer": "1",
         "rounds": [[{"answer": {"value": "2"}}]]},
        {"task_id": "b", "status": "failed", "reference": "1", "answer": None,
         "rounds": [[{"answer": {"value": "1"}}]]},
    ])
    vote = evaluate(tmp_path)["first_round_vote"]
    assert vote["available"] == 1
    assert vote["accuracy"] == 0
