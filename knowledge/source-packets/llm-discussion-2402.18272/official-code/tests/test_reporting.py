import json

import pytest

from llm_discussion.reporting import evaluate_suite


def write_suite(directory, conditions, ids):
    (directory / "suite.json").write_text(json.dumps({
        "experiments": list(conditions), "task_ids": ids, "synthetic": False,
    }))
    for name, records in conditions.items():
        child = directory / name
        child.mkdir()
        (child / "manifest.json").write_text(json.dumps({
            "task_ids": ids, "synthetic": False, "dataset_sha256": "same",
            "prompts_sha256": "same", "config": {"model": {"model": name}},
        }))
        (child / "results.jsonl").write_text("\n".join(json.dumps(r) for r in records))


def record(task_id, answer, **fields):
    return {"task_id": task_id, "answer": answer, "status": "completed",
            "reference": "A", "answer_type": "choice", **fields}


def test_all_homogeneous_and_mixed_comparisons_use_completed_labeled_pairs(tmp_path):
    baseline = [record("a", "B"), record("b", "A"), record("c", None, status="failed"),
                record("e", "A", reference=None)]
    discussion = [record("a", "A"), record("b", "B"), record("c", "A"), record("d", "A"),
                  record("e", "B", reference=None)]
    conditions = {"cmd-mixed": discussion}
    for i in range(1, 4):
        conditions[f"single-{i}"] = baseline
        conditions[f"cmd-{i}"] = discussion
    write_suite(tmp_path, conditions, list("abcde"))
    pairs = evaluate_suite(tmp_path)["paired"]
    assert len(pairs) == 9
    for i in range(1, 4):
        expected = {"both_completed": 2, "improved": 1, "regressed": 1, "unchanged": 0,
                    "excluded_failed_or_pending": 2, "excluded_unlabeled": 1}
        assert pairs[f"cmd-{i} vs single-{i}"] == expected
        assert pairs[f"cmd-mixed vs single-{i}"] == expected
        assert pairs[f"cmd-mixed vs cmd-{i}"] == {
            "both_completed": 4, "improved": 0, "regressed": 0, "unchanged": 4,
            "excluded_failed_or_pending": 0, "excluded_unlabeled": 1,
        }


@pytest.mark.parametrize("field,changed", [
    ("reference", "B"), ("answer_type", "number"), ("metric", "mra"), ("question", "different"),
])
def test_homogeneous_comparison_rejects_mismatched_tasks_without_mixed_condition(tmp_path, field, changed):
    write_suite(tmp_path, {"single-1": [record("a", "A")],
                          "cmd-1": [record("a", "A", **{field: changed})]}, ["a"])
    with pytest.raises(ValueError, match=f"Cannot pair different tasks: a \\({field}\\)"):
        evaluate_suite(tmp_path)


@pytest.mark.parametrize("condition,agents,overrides,expected_model,expected_routes", [
    ("single-1", 1, {}, "vendor/default", {"A": "vendor/default"}),
    ("cmd-mixed", 2, {"B": {"model": "vendor/other"}}, "mixed",
     {"A": "vendor/default", "B": "vendor/other"}),
    ("cmd-mixed", 2, {"A": {"model": "vendor/other", "temperature": 0},
                      "B": {"model": "vendor/other", "temperature": 1}},
     "vendor/other", {"A": "vendor/other", "B": "vendor/other"}),
])
def test_model_label_uses_actual_participant_routes(
    tmp_path, condition, agents, overrides, expected_model, expected_routes,
):
    write_suite(tmp_path, {condition: [record("a", "A")]}, ["a"])
    path = tmp_path / condition / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["config"] = {
        "model": {"model": "vendor/default"}, "discussion": {"agents": agents},
        "agent_models": overrides, "secretary_model": {"model": "vendor/secretary"},
    }
    path.write_text(json.dumps(manifest))

    report = evaluate_suite(tmp_path)["experiments"][condition]
    assert report["model"] == expected_model
    assert report["agent_models"] == expected_routes
    assert report["secretary_model"] == "vendor/secretary"
