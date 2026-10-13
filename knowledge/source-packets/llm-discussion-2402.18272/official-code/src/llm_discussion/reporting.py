"""Compare matched samples, keeping service failures distinct from reasoning changes."""

import json
from pathlib import Path

from .prompts import agent_name
from .storage import evaluate, read_manifest, read_results, record_score


def _paired(discussion: dict, baseline: dict, planned: list[str]) -> dict:
    common = sorted(set(baseline) & set(discussion))
    for task_id in common:
        for key in ("reference", "answer_type", "metric", "question"):
            if baseline[task_id].get(key) != discussion[task_id].get(key):
                raise ValueError(f"Cannot pair different tasks: {task_id} ({key})")
    completed = [i for i in common
                 if baseline[i]["status"] == discussion[i]["status"] == "completed"]
    usable = [i for i in completed if baseline[i].get("reference") is not None]
    improved = sum(record_score(discussion[i]) > record_score(baseline[i]) for i in usable)
    regressed = sum(record_score(discussion[i]) < record_score(baseline[i]) for i in usable)
    return {
        "both_completed": len(usable), "improved": improved, "regressed": regressed,
        "unchanged": len(usable) - improved - regressed,
        "excluded_failed_or_pending": len(planned) - len(completed),
        "excluded_unlabeled": len(completed) - len(usable),
    }


def evaluate_suite(directory: Path) -> dict:
    suite = json.loads((directory / "suite.json").read_text(encoding="utf-8"))
    manifests = {name: read_manifest(directory / name) for name in suite["experiments"]}
    expected = next(iter(manifests.values()))
    for name, manifest in manifests.items():
        for key in ("task_ids", "synthetic"):
            if manifest.get(key) != suite.get(key):
                raise ValueError(f"Suite {key} differs in {name}")
        for key in ("dataset_sha256", "image_sha256", "prompts_sha256", "sampling"):
            if manifest.get(key) != expected.get(key):
                raise ValueError(f"Suite {key} differs in {name}")
    reports = {name: evaluate(directory / name) for name in suite["experiments"]}
    result = {"synthetic": suite["synthetic"], "experiments": reports, "paired": {}}
    for name, report in reports.items():
        config = manifests[name]["config"]
        overrides = config.get("agent_models", {})
        agents = {
            agent_name(i): overrides.get(agent_name(i), config["model"])["model"]
            for i in range(config.get("discussion", {}).get("agents", 1))
        }
        models = set(agents.values())
        # Classify participant models; secretary routing is recorded separately.
        report["model"] = next(iter(models)) if len(models) == 1 else "mixed"
        report["agent_models"] = agents
        report["secretary_model"] = (config.get("secretary_model") or config["model"])["model"]
    if suite["synthetic"]:
        return result
    records = {name: read_results(directory / name) for name in reports}
    comparisons = [(name.replace("single-", "cmd-"), name)
                   for name in reports if name.startswith("single-")
                   and name.replace("single-", "cmd-") in reports]
    if "cmd-mixed" in reports:
        comparisons.extend(("cmd-mixed", name) for name in reports if name != "cmd-mixed")
    for discussion, baseline in comparisons:
        result["paired"][f"{discussion} vs {baseline}"] = _paired(
            records[discussion], records[baseline], suite["task_ids"])
    result["notice"] = "Small or incomplete runs do not establish an advantage. Paired comparisons exclude service failures."
    return result
