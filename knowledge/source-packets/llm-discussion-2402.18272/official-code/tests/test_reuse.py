from dataclasses import asdict, replace
import json
from pathlib import Path

import pytest

from llm_discussion.config import RunConfig
from llm_discussion.openrouter import ModelConfig
from llm_discussion.reuse import seed_suite
from llm_discussion.storage import evaluate, image_fingerprints, make_manifest, prepare_run, read_attempts, read_manifest
from llm_discussion.types import DiscussionConfig, Task


@pytest.fixture
def pilot(tmp_path):
    image = tmp_path / "image.png"
    image.write_bytes(b"original image")
    tasks = [Task("a", "Question A", "1", images=(str(image),)),
             Task("b", "Question B", "2"), Task("c", "Question C", "3")]
    model = ModelConfig("test/model")
    config = RunConfig(DiscussionConfig(agents=1, group_size=1, rounds=1), model, {}, model)
    configs = {"single-1": config, "single-2": config}
    source = tmp_path / "pilot"
    for name, config in configs.items():
        manifest = make_manifest(config, tasks[:2], synthetic=False, scenario=None,
                                 source="original.jsonl", data_hash="dataset-hash")
        manifest.update(sampling={"seed": 42, "index": None}, image_sha256=image_fingerprints(tasks[:2]))
        prepare_run(source / name, manifest)
        records = []
        for task, status, cost in [(tasks[0], "failed", .1), (tasks[0], "completed", .2),
                                   (tasks[1], "failed", .3)]:
            fields = {key: value for key, value in asdict(task).items()
                      if key in {"question", "reference", "answer_type", "category", "metric"}}
            records.append(dict(fields, task_id=task.id, status=status,
                                answer=task.reference if status == "completed" else None,
                                calls=[{"completion": {"usage": {"cost": cost}}}]))
        (source / name / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    (source / "suite.json").write_text(json.dumps({
        "experiments": list(configs), "task_ids": ["a", "b"], "synthetic": False,
    }))
    return source, tmp_path / "full", configs, tasks


def seed(pilot, **overrides):
    values = dict(data_hash="dataset-hash", source_label="full.jsonl",
                  sampling={"seed": None, "index": None}, execution={"request_concurrency": 24})
    values.update(overrides)
    return seed_suite(*pilot, **values)


def test_expansion_keeps_completed_history_costs_and_pilot_unchanged(pilot):
    source, target, _, _ = pilot
    before = {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}
    assert seed(pilot) == {"single-1": 1, "single-2": 1}
    manifest = read_manifest(target / "single-1")
    assert manifest["task_ids"] == ["a", "b", "c"]
    assert manifest["sampling"] == {"seed": None, "index": None}
    assert prepare_run(target / "single-1", manifest, resume=True) == {"a"}
    assert [record["status"] for record in read_attempts(target / "single-1")] == ["failed", "completed"]
    report = evaluate(target / "single-1")
    assert report["completed"] == 1 and report["pending"] == 2
    assert report["usage"]["cost"] == pytest.approx(.3)
    provenance = json.loads((target / "reused_conditions.json").read_text())
    assert provenance["conditions"]["single-1"]["copied_attempts"] == 2
    assert provenance["conditions"]["single-1"]["original_manifest"]["task_ids"] == ["a", "b"]
    assert before == {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}


@pytest.mark.parametrize("field,value", [
    ("config_sha256", "changed"), ("prompts_sha256", "changed"),
    ("dataset_sha256", "changed"), ("synthetic", True),
    ("sampling", {"seed": 100}), ("task_ids", ["a"]), ("image_sha256", {}),
])
def test_rejects_incompatible_later_condition_before_creating_target(pilot, field, value):
    source, target, _, _ = pilot
    path = source / "single-2" / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest[field] = value
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        seed(pilot)
    assert not target.exists()


@pytest.mark.parametrize("field,value", [
    ("task_id", "unknown"), ("question", "changed"), ("reference", "100"),
    ("answer_type", "choice"), ("category", "changed"), ("metric", "mra"),
])
def test_rejects_inconsistent_saved_task_even_in_earlier_failed_attempt(pilot, field, value):
    source, target, _, _ = pilot
    path = source / "single-2" / "results.jsonl"
    records = read_attempts(path.parent)
    records[0][field] = value
    path.write_text("".join(json.dumps(record) + "\n" for record in records))
    with pytest.raises(ValueError):
        seed(pilot)
    assert not target.exists()


def test_rejects_modified_images_and_config(pilot):
    source, target, configs, tasks = pilot
    configs["single-2"] = replace(configs["single-2"], model=ModelConfig("different/model"))
    with pytest.raises(ValueError, match="config"):
        seed(pilot)
    assert not target.exists()
    configs["single-2"] = configs["single-1"]
    Path(tasks[0].images[0]).write_bytes(b"different image")
    with pytest.raises(ValueError, match="image"):
        seed(pilot)
    assert not target.exists()


def test_rejects_overwriting_target_and_missing_pilot_tasks(pilot):
    source, target, configs, tasks = pilot
    with pytest.raises(ValueError, match="contained"):
        seed((source, target, configs, tasks[1:]))
    target.mkdir()
    marker = target / "keep"
    marker.write_text("unchanged")
    with pytest.raises(ValueError, match="exists"):
        seed(pilot)
    assert marker.read_text() == "unchanged"


def test_latest_failure_and_pending_tasks_are_not_reused(pilot):
    source, target, _, _ = pilot
    path = source / "single-1" / "results.jsonl"
    records = read_attempts(path.parent)
    # A previous success does not override a later failure; B has no attempt.
    records = [records[1], records[0]]
    path.write_text("".join(json.dumps(record) + "\n" for record in records))
    counts = seed(pilot)
    assert counts == {"single-1": 0, "single-2": 1}
    assert read_attempts(target / "single-1") == []
    assert evaluate(target / "single-1")["pending"] == 3


def test_selected_reuse_preserves_costs_and_initializes_changed_conditions_empty(pilot):
    source, target, configs, _ = pilot
    configs["single-2"] = replace(configs["single-2"], model=ModelConfig("different/model"))
    # Unselected histories are neither read nor copied.
    (source / "single-2" / "results.jsonl").write_text("unused incomplete record")
    assert seed(pilot, conditions=["single-1"]) == {"single-1": 1, "single-2": 0}
    assert evaluate(target / "single-1")["usage"]["cost"] == pytest.approx(.3)
    assert read_attempts(target / "single-2") == []
    manifest = read_manifest(target / "single-2")
    assert manifest["config"] == asdict(configs["single-2"])
    assert prepare_run(target / "single-2", manifest, resume=True) == set()
    assert json.loads((target / "suite.json").read_text())["experiments"] == list(configs)
    provenance = json.loads((target / "reused_conditions.json").read_text())
    assert provenance["selected_conditions"] == ["single-1"]
    assert provenance["initialized_conditions"] == ["single-2"]
    assert set(provenance["conditions"]) == {"single-1"}


def test_selected_reuse_rejects_invalid_selection_and_changed_selected_config(pilot):
    _, target, configs, _ = pilot
    for selection in ([], ["unknown"], "single-1"):
        with pytest.raises(ValueError, match="Reuse conditions"):
            seed(pilot, conditions=selection)
        assert not target.exists()
    configs["single-1"] = replace(configs["single-1"], model=ModelConfig("different/model"))
    with pytest.raises(ValueError, match="config"):
        seed(pilot, conditions=["single-1"])
    assert not target.exists()
