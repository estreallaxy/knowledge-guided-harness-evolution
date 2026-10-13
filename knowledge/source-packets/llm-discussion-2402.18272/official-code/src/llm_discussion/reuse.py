"""Seed a larger evaluation from compatible, completed pilot tasks."""

import hashlib
import json
from pathlib import Path

from .storage import image_fingerprints, make_manifest, prepare_run, read_attempts, read_manifest


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def seed_suite(source: Path, target: Path, configs: dict, tasks: list, *,
               data_hash: str, source_label: str, sampling: dict, execution: dict,
               conditions=None) -> dict[str, int]:
    """Reuse completed task histories without modifying or relaxing the pilot manifests.

    Every reused condition is validated before creating the target. By default all
    conditions are reused; an explicit subset leaves other conditions empty under
    their new configuration. Pending tasks and tasks whose latest attempt failed
    are left for the new run. Earlier failed attempts of reused tasks are retained
    so their recorded costs remain accounted for.
    """
    source, target = Path(source), Path(target)
    if target.exists():
        raise ValueError(f"Output already exists: {target}")
    task_map = {task.id: task for task in tasks}
    if not tasks or len(task_map) != len(tasks):
        raise ValueError("Target tasks must be nonempty and have unique IDs")
    if not configs or any(name in {"", ".", ".."} or Path(name).name != name for name in configs):
        raise ValueError("Condition names must be nonempty directory names")
    if isinstance(conditions, str):
        raise ValueError("Reuse conditions must be a collection of condition names")
    selected_conditions = set(configs if conditions is None else conditions)
    if not selected_conditions or not selected_conditions <= set(configs):
        raise ValueError("Reuse conditions must be a nonempty subset of configured conditions")
    suite_path = source / "suite.json"
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    names = suite["experiments"]
    if len(names) != len(set(names)) or set(names) != set(configs) or suite.get("synthetic") is not False:
        raise ValueError("Source suite conditions or synthetic flag differ")
    source_ids = suite["task_ids"]
    if not source_ids or len(source_ids) != len(set(source_ids)) or not set(source_ids) <= set(task_map):
        raise ValueError("Source task IDs must be unique and contained in the target")
    assets = image_fingerprints(tasks)
    source_assets = {image: assets[image] for task_id in source_ids for image in task_map[task_id].images}
    prepared, counts, provenance = {}, {}, {}
    original_sampling = None
    for name, config in configs.items():
        directory = source / name
        manifest = make_manifest(config, tasks, synthetic=False, scenario=None,
                                 source=source_label, data_hash=data_hash)
        if name not in selected_conditions:
            manifest.update(sampling=sampling, execution=execution, image_sha256=assets)
            prepared[name], counts[name] = (manifest, []), 0
            continue
        saved = read_manifest(directory)
        for key, expected in manifest.items():
            if key not in {"task_ids", "source"} and saved.get(key) != expected:
                raise ValueError(f"Cannot reuse {name}: {key} differs")
        if saved.get("task_ids") != source_ids or saved.get("image_sha256") != source_assets:
            raise ValueError(f"Cannot reuse {name}: task IDs or image fingerprints differ")
        if not isinstance(saved.get("sampling"), dict):
            raise ValueError(f"Cannot reuse {name}: sampling must be an object")
        if original_sampling is None:
            original_sampling = saved["sampling"]
        elif saved["sampling"] != original_sampling:
            raise ValueError(f"Cannot reuse {name}: source sampling differs between conditions")
        result_path = directory / "results.jsonl"
        results_hash = _sha(result_path)
        attempts = read_attempts(directory)
        if _sha(result_path) != results_hash:
            raise ValueError(f"Cannot reuse {name}: source results changed during validation")
        for record in attempts:
            task_id = record.get("task_id")
            if task_id not in source_ids:
                raise ValueError(f"Cannot reuse {name}: unknown result task ID")
            task = task_map[task_id]
            for field in ("question", "reference", "answer_type", "category", "metric"):
                if field not in record or record[field] != getattr(task, field):
                    raise ValueError(f"Cannot reuse {name}: result {field} differs for {task_id}")
            if record.get("status") not in {"completed", "failed"}:
                raise ValueError(f"Cannot reuse {name}: unknown result status")
        latest = {record["task_id"]: record for record in attempts}
        completed = {task_id for task_id, record in latest.items() if record["status"] == "completed"}
        selected = [record for record in attempts if record["task_id"] in completed]
        manifest.update(sampling=sampling, execution=execution, image_sha256=assets)
        prepared[name] = manifest, selected
        counts[name] = len(completed)
        provenance[name] = {
            "source": str(directory.resolve()),
            "manifest_sha256": _sha(directory / "manifest.json"),
            "results_sha256": results_hash, "original_manifest": saved,
            "copied_task_ids": [task_id for task_id in source_ids if task_id in completed],
            "copied_tasks": len(completed), "copied_attempts": len(selected),
        }
    # Validation above is read-only, including when a later condition is incompatible.
    target.mkdir(parents=True)
    for name, (manifest, attempts) in prepared.items():
        prepare_run(target / name, manifest)
        with (target / name / "results.jsonl").open("w", encoding="utf-8") as handle:
            for record in attempts:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    _write_json(target / "suite.json", {
        "experiments": list(configs), "task_ids": list(task_map), "synthetic": False,
    })
    _write_json(target / "reused_conditions.json", {
        "source": str(source.resolve()), "suite_sha256": _sha(suite_path),
        "selected_conditions": [name for name in configs if name in selected_conditions],
        "initialized_conditions": [name for name in configs if name not in selected_conditions],
        "conditions": provenance,
        "notice": "Completed pilot task histories reused; costs include earlier attempts. Pilot unchanged.",
    })
    return counts
