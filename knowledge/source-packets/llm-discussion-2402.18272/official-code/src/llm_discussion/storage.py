"""Persist complete experiment settings, append results, and score finished runs."""

from dataclasses import asdict
from datetime import datetime, timezone
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from . import __version__, prompts
from .answers import normalize_number


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def image_fingerprints(tasks) -> dict[str, str]:
    fingerprints = {}
    for task in tasks:
        for image in task.images:
            if image not in fingerprints:
                if urlsplit(image).scheme in ("http", "https"):
                    fingerprints[image] = "remote URL; content not pinned"
                else:
                    hasher = hashlib.sha256()
                    with Path(image).open("rb") as handle:
                        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                            hasher.update(chunk)
                    fingerprints[image] = hasher.hexdigest()
    return fingerprints


def read_manifest(directory: Path) -> dict:
    return json.loads((directory / "manifest.json").read_text(encoding="utf-8"))


def read_attempts(directory: Path) -> list[dict]:
    records = []
    with (directory / "results.jsonl").open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON in results.jsonl at line {number}") from error
            records.append(record)
    return records


def read_results(directory: Path) -> dict[str, dict]:
    return {record["task_id"]: record for record in read_attempts(directory)}


def make_manifest(config, tasks, *, synthetic, scenario, source, data_hash):
    settings = asdict(config)
    return {
        "format_version": 1, "package_version": __version__,
        "config": settings, "config_sha256": digest(settings),
        "prompts_sha256": hashlib.sha256(Path(prompts.__file__).read_bytes()).hexdigest(),
        "dataset_sha256": data_hash, "source": source, "task_ids": [t.id for t in tasks],
        "synthetic": synthetic, "scenario": scenario,
        "method": "single" if config.discussion.agents == config.discussion.rounds == 1 else "cmd",
    }


def prepare_run(directory: Path, manifest: dict, *, resume=False) -> set[str]:
    if resume:
        previous = read_manifest(directory)
        for key, value in manifest.items():
            if key not in {"source", "execution"} and previous.get(key) != value:
                raise ValueError(f"Cannot resume: {key} differs from the saved manifest")
        results = read_results(directory)
        if set(results) - set(manifest["task_ids"]):
            raise ValueError("Results contain task IDs absent from the manifest")
        return {task_id for task_id, record in results.items() if record["status"] == "completed"}
    if directory.exists():
        raise ValueError(f"Output already exists: {directory}; choose another directory or use --resume")
    directory.mkdir(parents=True)
    saved = dict(manifest, created_at=datetime.now(timezone.utc).isoformat())
    (directory / "manifest.json").write_text(json.dumps(saved, indent=2) + "\n", encoding="utf-8")
    (directory / "results.jsonl").touch()
    return set()


def append_result(directory: Path, result) -> None:
    with (directory / "results.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")
        handle.flush()


def score_answer(record, answer) -> float:
    """Score an already parsed answer; missing/failed answers always receive zero."""
    if answer is None or record.get("reference") is None:
        return 0.0
    try:
        if record.get("answer_type", "number") == "choice":
            return float(str(answer).strip().upper() == str(record["reference"]).strip().upper())
        predicted = Decimal(normalize_number(answer))
        expected = Decimal(normalize_number(record["reference"]))
        if record.get("metric", "exact") == "mra":
            if expected == 0:
                return float(predicted == 0)
            relative = abs(predicted - expected) / abs(expected)
            return sum(relative <= Decimal(i) / 100 for i in range(5, 51, 5)) / 10
        return float(predicted == expected)
    except ValueError:
        return 0.0


def record_score(record) -> float:
    return score_answer(record, record.get("answer")) if record["status"] == "completed" else 0.0


def first_round_vote(record):
    """A diagnostic from saved independent answers; abstain on plurality ties."""
    rounds = record.get("rounds", [])
    if not rounds or not rounds[0]:
        return None
    votes = Counter(opinion["answer"]["value"] for opinion in rounds[0])
    winners = [answer for answer, count in votes.items() if count == max(votes.values())]
    return winners[0] if len(winners) == 1 else None


def discussion_changes(records: list[dict]) -> dict | None:
    """Compare saved independent votes with final answers on the same completed tasks."""
    completed = [r for r in records if r["status"] == "completed"
                 and r.get("reference") is not None and r.get("metric", "exact") == "exact"
                 and len(r.get("rounds", [])) > 1 and r["rounds"][0]]
    if not completed:
        return None
    changes = Counter()
    tied_correct = ties = 0
    for record in completed:
        initial = first_round_vote(record)
        final_correct = bool(record_score(record))
        if initial is None:
            ties += 1
            tied_correct += final_correct
            continue
        initial_correct = bool(score_answer(record, initial))
        changes[f"{'correct' if initial_correct else 'wrong'}_to_{'correct' if final_correct else 'wrong'}"] += 1
    return {
        "completed_exact_tasks": len(completed), "compared_unique_votes": len(completed) - ties,
        **{key: changes[key] for key in ("wrong_to_correct", "correct_to_wrong", "correct_to_correct", "wrong_to_wrong")},
        "initial_ties": ties, "final_correct_after_initial_tie": tied_correct,
        "notice": "Diagnostic only: the initial vote uses the same agents before discussion; ties are separate. Failed and pending tasks excluded.",
    }


def evaluate(directory: Path) -> dict:
    manifest, records = read_manifest(directory), read_results(directory)
    planned = set(manifest["task_ids"])
    if set(records) - planned:
        raise ValueError("Results contain task IDs absent from the manifest")
    result = {
        "synthetic": manifest["synthetic"], "tasks": len(planned),
        "completed": sum(r["status"] == "completed" for r in records.values()),
        "failed": sum(r["status"] != "completed" for r in records.values()),
        "pending": len(planned - set(records)), "accuracy": None,
    }
    attempts = read_attempts(directory)
    calls = [call for record in attempts for call in record.get("calls", [])]
    usage = Counter()
    for call in calls:
        usage.update((call.get("completion") or {}).get("usage", {}))
    result.update(task_attempts=len(attempts), calls=len(calls), failed_calls=sum(c.get("error") is not None for c in calls),
                  usage=dict(usage), secretaries=sum(bool(r.get("used_secretary")) for r in records.values()))
    result["calls_without_usage"] = sum(not (c.get("completion") or {}).get("usage") for c in calls)
    if manifest["synthetic"]:
        result["notice"] = "Synthetic answers cannot be used as benchmark accuracy."
    elif result["pending"]:
        result["notice"] = "Run is incomplete: some planned tasks have no result."
    else:
        labeled = [r for r in records.values() if r.get("reference") is not None]
        exact = [r for r in labeled if r.get("metric", "exact") == "exact"]
        mra = [r for r in labeled if r.get("metric") == "mra"]
        correct = sum(record_score(r) for r in exact)
        completed_exact = [r for r in exact if r["status"] == "completed"]
        result.update(labeled_tasks=len(labeled), exact_tasks=len(exact), correct=int(correct),
                      accuracy=correct / len(exact) if exact else None,
                      completed_accuracy=(sum(record_score(r) for r in completed_exact) / len(completed_exact)
                                          if completed_exact else None),
                      notice="Latest attempt per task; failed labeled tasks count as incorrect.")
        if mra:
            result["mra"] = sum(record_score(r) for r in mra) / len(mra)
        categories = sorted({r.get("category") or "uncategorized" for r in labeled})
        result["categories"] = {}
        for category in categories:
            subset = [r for r in labeled if (r.get("category") or "uncategorized") == category]
            result["categories"][category] = {
                "tasks": len(subset), "mean_score": sum(record_score(r) for r in subset) / len(subset),
            }
        initial = [r for r in completed_exact if r.get("rounds") and r["rounds"][0]]
        if initial:
            result["first_round_vote"] = {
                "available": len(initial),
                "ties": sum(first_round_vote(r) is None for r in initial),
                "accuracy": sum(score_answer(r, first_round_vote(r)) for r in initial) / len(initial),
                "notice": "Diagnostic only: ties abstain; no secretary call. Failed tasks and missing initial rounds excluded.",
            }
    if not manifest["synthetic"]:
        changes = discussion_changes(list(records.values()))
        if changes is not None:
            result["discussion_changes"] = changes
    return result
