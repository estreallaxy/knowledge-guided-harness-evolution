#!/usr/bin/env python3
"""Export a final report for the three-dataset, seven-condition evaluation campaign."""

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys

from llm_discussion.reporting import evaluate_suite
from llm_discussion.storage import digest, first_round_vote, read_attempts, read_manifest


DATASETS = ("mindcube", "aime2025", "aime2026")
EXPECTED_QUESTIONS = {"mindcube": 1050, "aime2025": 30, "aime2026": 30}
CONDITIONS = ("single-1", "cmd-1", "single-2", "cmd-2", "single-3", "cmd-3", "cmd-mixed")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ACCOUNTING = (
    "Costs sum usage.cost from all saved call attempts, including failed attempts and reused histories. "
    "They exclude unsaved in-flight calls and earlier probes or calibration histories not copied into these suites. "
    "This is a saved-call ledger, not the account invoice. Missing cost metadata is not treated as proof of zero cost."
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def file_state(path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


def public_paths(value):
    """Make checkout-local path values portable without changing raw evidence."""
    if isinstance(value, dict):
        return {key: public_paths(item) for key, item in value.items()}
    if isinstance(value, list):
        return [public_paths(item) for item in value]
    if isinstance(value, str) and Path(value).is_absolute():
        try:
            return Path(value).resolve().relative_to(REPOSITORY_ROOT).as_posix()
        except ValueError:
            pass
    return value


def compact_reuse(path):
    if not path.exists():
        return None
    reuse = read_json(path)
    return {
        "source": reuse["source"], "file_sha256": sha256(path),
        "conditions": {name: {key: value for key, value in entry.items()
                               if key != "original_manifest"}
                       for name, entry in reuse["conditions"].items()},
        "notice": reuse.get("notice"),
    }


def calibration_ledgers(directory):
    path = directory / "calibration.json"
    if not path.exists():
        return {}
    return {(dataset, condition): Path(entry["archive"]) / condition / "results.jsonl"
            for dataset, entry in read_json(path).items()
            for condition in entry["experiments"]}


def summarize_calibration(directory, ledgers):
    """Count archived preparation calls once, excluding exactly copied histories."""
    conditions = []
    for (dataset, condition), path in ledgers.items():
        if dataset not in DATASETS or condition not in CONDITIONS:
            raise ValueError(f"Unknown calibration condition: {dataset}/{condition}")
        saved = Counter(digest(record) for record in read_attempts(directory / dataset / condition))
        usage = Counter()
        calls = reused_calls = missing_cost = 0
        for record in read_attempts(path.parent):
            fingerprint = digest(record)
            if saved[fingerprint]:
                saved[fingerprint] -= 1
                reused_calls += len(record.get("calls", []))
                continue
            for call in record.get("calls", []):
                call_usage = (call.get("completion") or {}).get("usage", {})
                usage.update(call_usage)
                calls += 1
                missing_cost += "cost" not in call_usage
        conditions.append({"dataset": dataset, "condition": condition, "source": str(path),
                           "results_sha256": sha256(path), "already_counted_calls": reused_calls,
                           "additional_calls": calls, "calls_without_cost": missing_cost,
                           "additional_usage": dict(usage)})
    return {"conditions": conditions,
            "additional_calls": sum(c["additional_calls"] for c in conditions),
            "additional_recorded_cost": sum(c["additional_usage"].get("cost", 0) for c in conditions),
            "calls_without_cost": sum(c["calls_without_cost"] for c in conditions)}


def summarize_dataset(directory):
    suite = read_json(directory / "suite.json")
    if suite.get("synthetic") is not False:
        raise ValueError(f"Cannot publish synthetic benchmark results: {directory}")
    if set(suite["experiments"]) != set(CONDITIONS) or len(suite["experiments"]) != len(CONDITIONS):
        raise ValueError(f"Expected all seven conditions: {directory}")
    ids = suite["task_ids"]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError(f"Expected unique, nonempty planned task IDs: {directory}")
    if len(ids) != EXPECTED_QUESTIONS[directory.name]:
        raise ValueError(f"Full {directory.name} requires {EXPECTED_QUESTIONS[directory.name]} tasks, found {len(ids)}")
    paths = [directory / "suite.json"] + [directory / name / filename
             for name in CONDITIONS for filename in ("manifest.json", "results.jsonl")]
    before = {path: file_state(path) for path in paths}
    evaluation = evaluate_suite(directory)
    pending = {name: report["pending"] for name, report in evaluation["experiments"].items()
               if report["pending"]}
    if pending:
        raise ValueError(f"Cannot publish final report: pending tasks in {directory.name}: {pending}")

    evidence, rows = {}, {task_id: {"task_id": task_id} for task_id in ids}
    usage_by_model = {}
    for name in CONDITIONS:
        child = directory / name
        manifest = read_manifest(child)
        attempts = read_attempts(child)
        records = {record["task_id"]: record for record in attempts}
        calls = [call for record in attempts for call in record.get("calls", [])]
        failures = Counter(call["error"] for call in calls if call.get("error"))
        failure_types = Counter()
        for error, count in failures.items():
            kind = ("Invalid numeric answer" if error.startswith("ValueError: invalid numeric answer:") else
                    "Invalid JSON" if error.startswith("JSONDecodeError:") else error)
            failure_types[kind] += count
        for call in calls:
            completion = call.get("completion") or {}
            key = (completion.get("model") or "unknown", completion.get("provider") or "unknown")
            entry = usage_by_model.setdefault(key, {"model": key[0], "provider": key[1],
                                                    "calls": 0, "usage": Counter()})
            entry["calls"] += 1
            entry["usage"].update(completion.get("usage", {}))
        report = evaluation["experiments"][name]
        report["calls_without_cost"] = sum("cost" not in (c.get("completion") or {}).get("usage", {}) for c in calls)
        report["call_errors"] = dict(sorted(failures.items()))
        report["call_error_types"] = dict(sorted(failure_types.items()))
        report["secretary_calls"] = sum(c.get("request", {}).get("stage") == "secretary" for c in calls)
        evidence[name] = {
            "config": manifest["config"], "config_sha256": manifest.get("config_sha256"),
            "manifest_sha256": sha256(child / "manifest.json"),
            "results_sha256": sha256(child / "results.jsonl"),
            "execution": manifest.get("execution"),
        }
        for task_id, record in records.items():
            if record["status"] not in {"completed", "failed"}:
                raise ValueError(f"Nonterminal result status in {directory.name}/{name}: {task_id}")
            row = rows[task_id]
            row.update(category=record.get("category") or "uncategorized", gold=record.get("reference"))
            initial = first_round_vote(record)
            row.update({f"{name}.answer": record.get("answer"), f"{name}.status": record["status"],
                        f"{name}.initial_vote": initial if initial is not None else
                        ("TIE" if record.get("rounds") and record["rounds"][0] else "UNAVAILABLE")})
    if before != {path: file_state(path) for path in paths}:
        raise ValueError(f"Inputs changed while reading {directory}; wait for the campaign to stop")

    first = read_manifest(directory / CONDITIONS[0])
    provenance_path = Path(first["source"]).parent / "provenance.json" if first.get("source") else None
    provenance = None
    if provenance_path and provenance_path.exists():
        provenance = read_json(provenance_path)
        if provenance.get("tasks_sha256") != first.get("dataset_sha256"):
            raise ValueError(f"Dataset provenance hash differs from manifest: {directory}")
        provenance = {key: value for key, value in provenance.items() if key != "images"}
        provenance["provenance_file_sha256"] = sha256(provenance_path)
    evaluation["evidence"] = {
        "source_directory": str(directory.resolve()), "suite_sha256": sha256(directory / "suite.json"),
        "dataset_source": first.get("source"), "dataset_sha256": first.get("dataset_sha256"),
        "prompts_sha256": first.get("prompts_sha256"), "ordered_task_ids_sha256": digest(ids),
        "image_count": len(first.get("image_sha256", {})),
        "image_fingerprints_sha256": digest(first.get("image_sha256", {})),
        "sampling": first.get("sampling"), "conditions": evidence,
        "provenance": provenance, "reuse": compact_reuse(directory / "reused_conditions.json"),
    }
    evaluation["usage_by_model"] = list(usage_by_model.values())
    return evaluation, list(rows.values())


def table(headers, rows):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    return ["| " + " | ".join(map(cell, row)) + " |"
            for row in (headers, ["---"] * len(headers), *rows)] + [""]


def percentage(value):
    return "N/A" if value is None else f"{100 * value:.2f}%"


def render_report(summary):
    totals = summary["totals"]
    lines = ["# Full MindCube and AIME evaluation", "", f"Generated: {summary['generated_at']}", "",
             f"All **{totals['planned_task_conditions']:,} planned task/condition pairs** have a saved terminal attempt "
             f"across **{totals['dataset_questions']:,} questions**. Latest outcomes: "
             f"**{totals['completed']:,} completed, {totals['failed']:,} failed, 0 pending**. "
             "SAW-Bench and VSI-Bench are outside this evaluation.", "",
             f"The ledger contains **{totals['calls']:,} saved calls**, including retries, "
             f"with **${totals['usage'].get('cost', 0):.6f} recorded cost**. "
             f"{totals['calls_without_cost']:,} calls lack cost metadata. " + ACCOUNTING, "",
             "Latest failed labeled attempts count as incorrect in full accuracy. Completed-only accuracy is also shown. "
             "Paired comparisons exclude failed tasks and disclose the exclusions. "
             "These hosted-model experiments do not reproduce the paper's historical model scores.", ""]
    calibration = summary.get("calibration")
    if calibration and calibration["conditions"]:
        lines += ["## Preparation costs", "",
                  f"Archived output-limit calibration adds **${calibration['additional_recorded_cost']:.6f}** "
                  f"from **{calibration['additional_calls']:,} saved calls** not copied into the evaluated suites. "
                  f"Evaluation plus this calibration therefore records **${totals['recorded_cost_including_calibration']:.6f}**. "
                  "Exact copied attempt histories are excluded from this addition, so reused Luna calls are counted once. "
                  f"{calibration['calls_without_cost']:,} additional calls lack cost metadata. "
                  "Other earlier model probes remain outside this total.", ""]
        lines += table(["Dataset / condition", "Calls already in evaluation", "Additional calls", "Additional cost USD"],
                       [[f"{c['dataset']} / {c['condition']}", c["already_counted_calls"], c["additional_calls"],
                         f"${c['additional_usage'].get('cost', 0):.6f}"] for c in calibration["conditions"]])
    for dataset, result in summary["datasets"].items():
        reports, evidence = result["experiments"], result["evidence"]
        lines += [f"## {dataset}", "", f"Per-task gold answers, final answers, initial votes, and statuses: [{dataset}.csv]({dataset}.csv). "
                  "`TIE` means no unique initial plurality; `UNAVAILABLE` means no complete initial round was saved.", ""]
        lines += table(["Condition", "Correct / planned", "Accuracy", "Completed-only", "Failed / pending", "Task attempts", "Saved calls", "Secretary calls", "Cost USD"],
                       [[name, f"{r.get('correct', 0)} / {r['tasks']}", percentage(r["accuracy"]), percentage(r.get("completed_accuracy")),
                         f"{r['failed']} / {r['pending']}", r["task_attempts"], r["calls"], r["secretary_calls"], f"${r['usage'].get('cost', 0):.6f}"]
                        for name, r in reports.items()])
        lines += ["### Matched changes", "", "Both conditions must complete a labeled task to enter a pair. Changes compare scores on that same task.", ""]
        lines += table(["Comparison", "Compared", "Wrong → correct", "Correct → wrong", "Unchanged", "Excluded failed / pending", "Excluded unlabeled"],
                       [[name, r["both_completed"], r["improved"], r["regressed"], r["unchanged"], r["excluded_failed_or_pending"], r["excluded_unlabeled"]]
                        for name, r in result["paired"].items()])
        lines += ["### Independent first vote → final answer", "",
                  "This diagnostic uses the same agents' independent first round, with initial ties separate. "
                  "It measures changes across the complete CMD procedure, including any final secretary call; "
                  "it is not an isolated causal estimate of discussion benefit or a compute-matched self-consistency baseline. "
                  "Failed tasks are excluded.", ""]
        changes = [(name, r["discussion_changes"]) for name, r in reports.items() if r.get("discussion_changes")]
        lines += table(["Condition", "Unique votes", "Wrong → correct", "Correct → wrong", "Correct → correct", "Wrong → wrong", "Initial ties", "Final correct after tie"],
                       [[name, r["compared_unique_votes"], r["wrong_to_correct"], r["correct_to_wrong"], r["correct_to_correct"], r["wrong_to_wrong"], r["initial_ties"], r["final_correct_after_initial_tie"]]
                        for name, r in changes])
        lines += ["### Categories", ""]
        categories = sorted({category for r in reports.values() for category in r.get("categories", {})})
        lines += table(["Category", "Questions", *reports],
                       [[category, reports[CONDITIONS[0]]["categories"][category]["tasks"],
                         *[percentage(r["categories"][category]["mean_score"]) for r in reports.values()]]
                        for category in categories])
        lines += ["### Recorded settings and usage", "",
                  "The table reads each single-agent manifest; full per-condition configurations, including mixed-agent routing, "
                  "are preserved in `evaluation.json`. Provider prices below are routing ceilings in USD per million tokens, "
                  "not observed unit prices or a total dollar budget.", ""]
        profiles = [(name, evidence["conditions"][name]["config"]["model"]) for name in CONDITIONS if name.startswith("single-")]
        lines += table(["Condition / model", "Reasoning", "Completion limit", "Temperature", "Provider routing"],
                       [[f"{name}: {p['model']}", json.dumps(p.get("reasoning")), p.get("max_completion_tokens"), p.get("temperature"), json.dumps(p.get("provider"), sort_keys=True)]
                        for name, p in profiles])
        mixed = evidence["conditions"]["cmd-mixed"]["config"]
        lines += [f"CMD discussion settings: `{json.dumps(mixed.get('discussion'), sort_keys=True)}`. "
                  f"Mixed assignments: `{json.dumps({a: p['model'] for a, p in mixed.get('agent_models', {}).items()}, sort_keys=True)}`. "
                  f"Secretary: `{mixed.get('secretary_model', mixed['model'])['model']}`.", ""]
        lines += table(["Response model / provider", "Calls", "Prompt tokens", "Completion tokens", "Reasoning tokens", "Cost USD"],
                       [[f"{r['model']} / {r['provider']}", r["calls"], r["usage"].get("prompt_tokens", 0),
                         r["usage"].get("completion_tokens", 0), r["usage"].get("completion_tokens_details.reasoning_tokens", 0), f"${r['usage'].get('cost', 0):.6f}"]
                        for r in result["usage_by_model"]])
        lines += ["### Failed calls and provenance", ""]
        lines += table(["Condition", "Failed calls", "Without usage", "Without cost", "Recorded errors"],
                       [[name, r["failed_calls"], r["calls_without_usage"], r["calls_without_cost"],
                         "; ".join(f"{error}: {count}" for error, count in r["call_error_types"].items()) or "None"] for name, r in reports.items()])
        lines += [f"Dataset SHA-256: `{evidence['dataset_sha256']}`. "
                  f"Prompt-source SHA-256: `{evidence['prompts_sha256']}`. "
                  f"Ordered task-ID SHA-256: `{evidence['ordered_task_ids_sha256']}`. "
                  f"Images: {evidence['image_count']}; fingerprint-map SHA-256: `{evidence['image_fingerprints_sha256']}`.", ""]
        provenance = evidence["provenance"]
        if provenance:
            lines += [f"Source revision: `{provenance.get('source_revision', provenance.get('revision'))}`. "
                      f"License: `{provenance.get('license')}`. Full compact provenance and source-file hashes are in `evaluation.json`.", ""]
        reuse = evidence["reuse"]
        if reuse:
            lines += [f"Reused histories from `{reuse['source']}` are counted once in this ledger. "
                      f"Reuse-record SHA-256: `{reuse['file_sha256']}`.", ""]
            lines += table(["Condition", "Copied tasks", "Copied task attempts"],
                           [[name, entry["copied_tasks"], entry["copied_attempts"]] for name, entry in reuse["conditions"].items()])
    lines += ["## Interpretation and reproduction", "",
              "This is one generation per single-agent baseline and one CMD execution per task, with bounded retries for failures. "
              "Outputs were not rerun according to correctness. Luna disables API reasoning; Gemma disables API reasoning; "
              "Muse uses mandatory minimal reasoning. Model token limits can differ and are recorded above. "
              "Consequently this is not an equal-compute or uniformly reasoning-disabled comparison. "
              "The results alone do not establish statistical significance or universal discussion gains.", "",
              "Regenerate this report from the saved, quiescent campaign:", "", "```bash",
              "python scripts/summarize_evaluation.py --input runs/full-evaluation --output runs/full-evaluation/report", "```", "",
              "The exporter rejects pending tasks, synthetic suites, missing conditions, mismatched paired inputs, and ledgers that change while being read. "
              "It never loads credentials, repairs model answers, or makes API calls.", "",
              "Paths within the checkout are relative to the repository root in these public artifacts; external paths remain absolute. "
              "Raw manifests, ledgers, reuse records, and provenance files are unchanged, and recorded hashes refer to those original files.", ""]
    return "\n".join(lines)


def generate(input_directory, output_directory):
    status_path = input_directory / "campaign-status.json"
    if status_path.exists() and read_json(status_path).get("state") == "running":
        raise ValueError("Cannot publish final report while the campaign is running")
    inputs = [input_directory / dataset / name / filename for dataset in DATASETS
              for name in CONDITIONS for filename in ("manifest.json", "results.jsonl")]
    inputs.extend(input_directory / dataset / "suite.json" for dataset in DATASETS)
    calibration_paths = calibration_ledgers(input_directory)
    if (input_directory / "calibration.json").exists():
        inputs.append(input_directory / "calibration.json")
    inputs.extend(calibration_paths.values())
    before = {path: file_state(path) for path in inputs}
    summary = {"generated_at": datetime.now(timezone.utc).isoformat(), "accounting": ACCOUNTING, "datasets": {}}
    csvs = {}
    for name in DATASETS:
        summary["datasets"][name], rows = summarize_dataset(input_directory / name)
        handle = io.StringIO(newline="")
        headers = ["task_id", "category", "gold"] + [f"{condition}.{field}" for condition in CONDITIONS for field in ("answer", "initial_vote", "status")]
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        csvs[name] = handle.getvalue()
    totals = Counter()
    usage = Counter()
    for result in summary["datasets"].values():
        totals["dataset_questions"] += result["experiments"][CONDITIONS[0]]["tasks"]
        for report in result["experiments"].values():
            for field in ("completed", "failed", "pending", "calls", "failed_calls", "calls_without_cost",
                          "calls_without_usage", "task_attempts", "secretary_calls"):
                totals[field] += report[field]
            totals["planned_task_conditions"] += report["tasks"]
            usage.update(report["usage"])
    summary["totals"] = dict(totals, usage=dict(usage))
    summary["calibration"] = summarize_calibration(input_directory, calibration_paths)
    summary["totals"]["recorded_cost_including_calibration"] = (
        usage.get("cost", 0) + summary["calibration"]["additional_recorded_cost"]
    )
    summary = public_paths(summary)
    rendered = render_report(summary)
    if before != {path: file_state(path) for path in inputs}:
        raise ValueError("Campaign inputs changed while generating the report; wait for all writers to stop")
    # Validate every suite before creating or replacing any report artifacts.
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / "report.md").write_text(rendered, encoding="utf-8")
    (output_directory / "evaluation.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for name, content in csvs.items():
        (output_directory / f"{name}.csv").write_text(content, encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        summary = generate(args.input, args.output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary["totals"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
