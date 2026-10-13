#!/usr/bin/env python3
"""Run a bounded, resumable evaluation campaign from repository-relative paths."""

import argparse
import asyncio
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import sys

from llm_discussion.config import load_suite
from llm_discussion.cli import _select_tasks
from llm_discussion.data import load_tasks
from llm_discussion.storage import image_fingerprints, make_manifest, prepare_run


def load_plan(path):
    plan = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or set(plan) != {"config", "sample_seed", "requests_per_minute", "datasets"}:
        raise ValueError("Plan requires config, sample_seed, requests_per_minute, and datasets")
    load_suite(Path(plan["config"]))
    if type(plan["sample_seed"]) is not int:
        raise ValueError("sample_seed must be an integer")
    rpm = plan["requests_per_minute"]
    if type(rpm) not in (int, float) or not math.isfinite(rpm) or rpm < 0:
        raise ValueError("requests_per_minute must be finite and nonnegative")
    if not isinstance(plan["datasets"], list) or not plan["datasets"]:
        raise ValueError("datasets must be a nonempty list")
    names = set()
    fields = {"name", "path", "limit", "task_concurrency", "request_concurrency", "request_budget", "max_passes"}
    for dataset in plan["datasets"]:
        if not isinstance(dataset, dict) or not fields <= set(dataset) or set(dataset) - fields - {"config"}:
            raise ValueError("Each dataset requires " + ", ".join(sorted(fields)))
        name = dataset["name"]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name) or name in names:
            raise ValueError("Dataset names must be unique safe directory names")
        names.add(name)
        for key in fields - {"name", "path"}:
            if type(dataset[key]) is not int or dataset[key] < 1:
                raise ValueError(f"{name}: {key} must be a positive integer")
        if dataset["max_passes"] > 2:
            raise ValueError("At most two passes are supported")
        if "config" in dataset:
            load_suite(Path(dataset["config"]))
        if len(load_tasks(Path(dataset["path"]))) < dataset["limit"]:
            raise ValueError(f"{name}: limit exceeds available tasks")
    return plan


def request_count(directory):
    path = directory / "executions.jsonl"
    return sum(json.loads(line)["requests_started"] for line in path.read_text().splitlines() if line.strip()) if path.exists() else 0


def expected_manifests(plan, dataset):
    """Use the CLI's exact selection and fingerprint rules without loading .env."""
    configurations = load_suite(Path(dataset.get("config", plan["config"])))
    arguments = argparse.Namespace(dataset=Path(dataset["path"]), limit=dataset["limit"],
                                   sample_seed=plan["sample_seed"], index=None)
    tasks, data_hash, source = _select_tasks(arguments)
    images = image_fingerprints(tasks)
    return {name: dict(make_manifest(config, tasks, synthetic=False, scenario=None,
                                    source=source, data_hash=data_hash),
                       sampling={"seed": plan["sample_seed"], "index": None}, image_sha256=images)
            for name, config in configurations.items()}


def completed(directory, expected):
    suite_path = directory / "suite.json"
    if not suite_path.exists():
        return False
    suite = json.loads(suite_path.read_text())
    ids = next(iter(expected.values()))["task_ids"]
    if set(suite["experiments"]) != set(expected) or suite["task_ids"] != ids or suite["synthetic"]:
        raise ValueError(f"Saved suite does not match the planned real experiment: {directory}")
    all_complete = True
    for name, manifest in expected.items():
        child = directory / name
        if not (child / "manifest.json").exists():
            all_complete = False
            continue
        # The same validator as --resume checks config, source data, prompts,
        # ordered task IDs, image content, sampling, and synthetic/real status.
        all_complete &= prepare_run(child, manifest, resume=True) == set(ids)
    return all_complete


def timestamp():
    return datetime.now(timezone.utc).isoformat()


async def run_campaign(plan, output):
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".campaign.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError(f"Another campaign driver holds the lock: {output}") from error
        path = output / "campaign-status.json"
        fingerprint = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()
        state = json.loads(path.read_text()) if path.exists() else {
            "started_at": timestamp(), "plan_sha256": fingerprint, "datasets": {},
        }
        if state["plan_sha256"] != fingerprint:
            raise ValueError("Cannot resume a campaign with a changed plan")
        state.update(driver_pid=os.getpid(), state="running")

        def save():
            state["updated_at"] = timestamp()
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            temporary.replace(path)

        async def worker(dataset):
            name, directory = dataset["name"], output / dataset["name"]
            status = state["datasets"].setdefault(name, {"passes": []})
            status["request_budget"] = dataset["request_budget"]
            status["config"] = dataset.get("config", plan["config"])

            def refresh():
                # A killed invocation cannot report its exact final count. Charge its
                # whole allocation rather than silently resetting a spending guard.
                uncertain = sum(p["max_requests"] for p in status["passes"] if p.get("unaccounted", False))
                status["requests_consumed"] = request_count(directory) + uncertain
                return dataset["request_budget"] - status["requests_consumed"]

            try:
                expected = expected_manifests(plan, dataset)
                for previous in status["passes"]:
                    if "returncode" not in previous:
                        previous["unaccounted"] = True
                refresh()
                if completed(directory, expected):
                    status["state"] = "completed"
                    save()
                    return
                status["state"] = "incomplete"
                while len(status["passes"]) < dataset["max_passes"]:
                    remaining = refresh()
                    if remaining <= 0:
                        status["state"] = "budget_exhausted"
                        break
                    command = [sys.executable, "-m", "llm_discussion", "suite", "--config", status["config"],
                               "--dataset", dataset["path"], "--output", str(directory),
                               "--sample-seed", str(plan["sample_seed"]), "--requests-per-minute", str(plan["requests_per_minute"]),
                               "--max-requests", str(remaining)]
                    for key in ("limit", "task_concurrency", "request_concurrency"):
                        command.extend(["--" + key.replace("_", "-"), str(dataset[key])])
                    if directory.exists():
                        command.append("--resume")
                    attempt = {"started_at": timestamp(), "max_requests": remaining, "requests_before": request_count(directory)}
                    status["passes"].append(attempt)
                    status["state"] = "running"
                    save()
                    with (output / f"{name}.log").open("a") as log:
                        process = await asyncio.create_subprocess_exec(*command, stdout=log, stderr=asyncio.subprocess.STDOUT)
                        status["child_pid"] = process.pid
                        save()
                        try:
                            code = await process.wait()
                        except asyncio.CancelledError:
                            if process.returncode is None:
                                process.terminate()
                            try:
                                await asyncio.wait_for(process.wait(), 10)
                            except asyncio.TimeoutError:
                                process.kill()
                                await process.wait()
                            attempt["unaccounted"] = request_count(directory) == attempt["requests_before"]
                            raise
                    attempt.update(returncode=code, finished_at=timestamp())
                    attempt["unaccounted"] = code not in (0, 1, 2) and request_count(directory) == attempt["requests_before"]
                    status.update(returncode=code, child_pid=None)
                    refresh()
                    if completed(directory, expected):
                        status["state"] = "completed"
                        break
                    status["state"] = "incomplete" if code in (0, 1) else "error"
                    if code not in (0, 1):
                        break
                if refresh() <= 0 and status["state"] == "incomplete":
                    status["state"] = "budget_exhausted"
                save()
            except asyncio.CancelledError:
                status.update(state="interrupted", child_pid=None)
                refresh()
                save()
                raise
            except (OSError, ValueError, KeyError, TypeError) as error:
                status.update(state="error", error=str(error))
                save()

        save()
        workers = [asyncio.create_task(worker(dataset)) for dataset in plan["datasets"]]
        try:
            await asyncio.gather(*workers)
        except BaseException:
            for task in workers:
                task.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            state["state"] = "interrupted"
            save()
            raise
        state["state"] = "completed" if all(d["state"] == "completed" for d in state["datasets"].values()) else "incomplete"
        save()
        return 0 if state["state"] == "completed" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        plan = load_plan(args.plan)

        def interrupted(*_):
            raise KeyboardInterrupt

        signal.signal(signal.SIGTERM, interrupted)
        return asyncio.run(run_campaign(plan, args.output))
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
