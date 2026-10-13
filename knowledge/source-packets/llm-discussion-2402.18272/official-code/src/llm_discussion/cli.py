"""Run CMD with OpenRouter or synthetic agents, then inspect saved results."""

import argparse
import asyncio
from contextlib import AsyncExitStack
from dataclasses import asdict, fields
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import sys
import time
from uuid import uuid4

import httpx
from dotenv import load_dotenv

from .config import load_config, load_suite
from .data import load_tasks
from .engine import run_discussion
from .models import DryRunModel, RoutedModel
from .openrouter import OpenRouterModel
from .prompts import agent_name
from .scheduling import RequestBudget, Schedule, ScheduledModel, run_jobs
from .storage import append_result, digest, evaluate, image_fingerprints, make_manifest, prepare_run
from .types import DiscussionConfig, ModelError, Task


def _model(config, synthetic, scenario, client=None):
    if synthetic:
        return DryRunModel(scenario if config.discussion.agents > 1 else "consensus", config.discussion.agents)
    profiles = {agent_name(i): config.agent_models.get(agent_name(i), config.model)
                for i in range(config.discussion.agents)}
    profiles[agent_name(config.discussion.agents)] = config.secretary_model
    clients, routes = {}, {}
    for agent, profile in profiles.items():
        key = digest(asdict(profile))
        if key not in clients:
            clients[key] = OpenRouterModel(profile, client=client)
        routes[agent] = clients[key]
    return RoutedModel(routes)


def _select_tasks(args):
    if args.dataset:
        tasks = load_tasks(args.dataset)
        data_hash = hashlib.sha256(args.dataset.read_bytes()).hexdigest()
        source = str(args.dataset.resolve())
    else:
        question = args.question if args.question is not None else "What is 12 plus 7?"
        if not question.strip():
            raise ValueError("--question must not be empty")
        tasks = [Task("question-0", question)]
        data_hash, source = digest([asdict(t) for t in tasks]), "question"
    if args.limit < 1:
        raise ValueError("--limit must be positive")
    if args.index is not None:
        if not 0 <= args.index < len(tasks):
            raise ValueError(f"--index must be between 0 and {len(tasks) - 1}")
        tasks = [tasks[args.index]]
    else:
        if args.sample_seed is not None:
            # Shuffle within categories, then interleave them for balanced small probes.
            rng = random.Random(args.sample_seed)
            buckets = {}
            for task in tasks:
                buckets.setdefault(getattr(task, "category", None) or "uncategorized", []).append(task)
            for bucket in buckets.values():
                rng.shuffle(bucket)
            tasks = []
            while any(buckets.values()):
                for key in sorted(buckets):
                    if buckets[key]:
                        tasks.append(buckets[key].pop())
        tasks = tasks[:args.limit]
    return tasks, data_hash, source


async def _execute(args, experiments, *, suite=False):
    started_at = time.perf_counter()
    if args.resume and args.output is None:
        raise ValueError("--resume requires --output pointing to the existing run")
    selected = set(getattr(args, "conditions", None) or experiments)
    if selected - set(experiments):
        raise ValueError("Unknown conditions: " + ", ".join(sorted(selected - set(experiments))))
    synthetic = args.dry_run or all(c.model is None for c in experiments.values())
    if not synthetic and args.scenario is not None:
        raise ValueError("--scenario only applies to --dry-run")
    scenario = (args.scenario or "consensus") if synthetic else None
    tasks, data_hash, source = _select_tasks(args)
    assets = image_fingerprints(tasks)
    rpm = args.requests_per_minute
    if rpm is None:
        profiles = [p for c in experiments.values() for p in
                    (c.model, c.secretary_model, *c.agent_models.values()) if p]
        rpm = 18 if any(p.model.endswith(":free") for p in profiles) else 0
    schedule = Schedule(args.task_concurrency, args.request_concurrency,
                        0 if synthetic else rpm, args.max_requests)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output or Path("runs") / f"{stamp}-{uuid4().hex[:8]}"
    if args.resume and not output.is_dir():
        raise ValueError(f"Cannot resume: output does not exist: {output}")
    if suite and output.exists() and not args.resume:
        raise ValueError(f"Output already exists: {output}; choose another directory or use --resume")
    async with AsyncExitStack() as stack:
        client = None
        if not synthetic:
            load_dotenv(".env", override=False)
            client = await stack.enter_async_context(httpx.AsyncClient())
        # Validate every configured client (including credentials) before making files.
        budget = RequestBudget(schedule)
        models = {}
        for name, config in experiments.items():
            paced_agents = None
            if args.requests_per_minute is None and not synthetic:
                profiles = {agent_name(i): config.agent_models.get(agent_name(i), config.model)
                            for i in range(config.discussion.agents)}
                profiles[agent_name(config.discussion.agents)] = config.secretary_model
                paced_agents = {agent for agent, profile in profiles.items() if profile.model.endswith(":free")}
            models[name] = ScheduledModel(_model(config, synthetic, scenario, client), budget,
                                          paced_agents=paced_agents)
        completed, paths = {}, {}
        for name, config in experiments.items():
            manifest = make_manifest(config, tasks, synthetic=synthetic, scenario=scenario,
                                     source=source, data_hash=data_hash)
            manifest["sampling"] = {"seed": args.sample_seed, "index": args.index}
            manifest["image_sha256"] = assets
            # Scheduling may be adjusted on resume without changing model inputs.
            manifest["execution"] = dict(asdict(schedule),
                rate_scope="free_models" if args.requests_per_minute is None else "all_models",
                conditions=sorted(selected))
            paths[name] = output / name if suite else output
            completed[name] = prepare_run(paths[name], manifest,
                resume=args.resume if not suite else args.resume and (paths[name] / "manifest.json").exists())
            with (paths[name] / "invocations.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"started_at": stamp, "execution": manifest["execution"],
                                         "resume": args.resume}) + "\n")
        if suite:
            (output / "suite.json").write_text(json.dumps({
                "experiments": list(experiments), "task_ids": [t.id for t in tasks],
                "synthetic": synthetic,
            }, indent=2) + "\n", encoding="utf-8")
        failed = written = 0

        async def work(job):
            nonlocal written, failed
            name, task = job
            if budget.exhausted:
                return
            result = await run_discussion(task, models[name], experiments[name].discussion)
            # No await during append: one complete JSONL record per finished task.
            append_result(paths[name], result)
            written += 1
            failed += result.status != "completed"
            print(json.dumps({"experiment": name, "task": task.id,
                              "status": result.status, "requests_started": budget.started}),
                  file=sys.stderr, flush=True)

        jobs = ((name, task) for task in tasks for name in experiments
                if name in selected and task.id not in completed[name])
        await run_jobs(jobs, work, schedule.task_concurrency)
    summary = {"output": str(output), "synthetic": synthetic, "written": written,
               "skipped_completed": sum(map(len, completed.values())), "failed": failed,
               "requests_started": budget.started, "request_budget_exhausted": budget.exhausted}
    summary["elapsed_seconds"] = round(time.perf_counter() - started_at, 3)
    unfinished = sum(report["failed"] + report["pending"]
                     for report in (evaluate(path) for path in paths.values()))
    summary["unfinished"] = unfinished
    with (output / "executions.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(summary, started_at=stamp)) + "\n")
    if suite:
        from .reporting import evaluate_suite
        report = evaluate_suite(output)
        (output / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    return 1 if unfinished else 0


async def _run(args) -> int:
    overrides = {f.name: getattr(args, f.name) for f in fields(DiscussionConfig)
                 if getattr(args, f.name) is not None}
    config = load_config(args.config, model=args.model, discussion_overrides=overrides)
    return await _execute(args, {"run": config})


async def _suite(args) -> int:
    return await _execute(args, load_suite(args.config), suite=True)


def _prepare(args):
    output = args.output or Path("data/benchmarks") / args.benchmark
    if args.benchmark == "mindcube":
        from .benchmarks.mindcube import prepare
        path = prepare(output, split=args.split, limit=args.limit)
    elif args.benchmark == "saw":
        from .benchmarks.spatial_video import prepare_saw
        path = prepare_saw(output, limit=args.limit, frames=args.frames)
    else:
        from .benchmarks.matharena import prepare_aime
        path = prepare_aime(output, year=int(args.benchmark[-4:]), limit=args.limit)
    print(json.dumps({"dataset": str(path)}))
    return 0


def _evaluate(args):
    if (args.run / "suite.json").exists():
        from .reporting import evaluate_suite
        report = evaluate_suite(args.run)
    else:
        report = evaluate(args.run)
    print(json.dumps(report, indent=2))
    return 0


def _inputs(parser):
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--dataset", type=Path)
    inputs.add_argument("--question")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--index", type=int)
    parser.add_argument("--sample-seed", type=int, help="Reproducible sampling balanced across categories")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scenario", choices=("consensus", "tie"))
    parser.add_argument("--task-concurrency", type=int, default=3)
    parser.add_argument("--request-concurrency", type=int, default=6)
    parser.add_argument("--requests-per-minute", type=float,
                        help="Shared rate for all requests; by default only free models are paced at 18/minute")
    parser.add_argument("--max-requests", type=int, help="Stop starting new requests at this per-invocation budget")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resume", action="store_true", help="Skip completed tasks and retry failed tasks")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Conquer-and-Merge Discussion with OpenRouter.")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Run a question or dataset; no model means an offline dry run")
    run.add_argument("--config", type=Path)
    run.add_argument("--model", help="Default OpenRouter model identifier (provider/model)")
    _inputs(run)
    for field in fields(DiscussionConfig):
        run.add_argument("--" + field.name.replace("_", "-"), type=int)
    run.set_defaults(handler=_run)
    suite = commands.add_parser("suite", help="Compare single, homogeneous CMD, and mixed CMD on identical tasks")
    suite.add_argument("--config", type=Path, required=True)
    suite.add_argument("--conditions", nargs="+", help="Run only these conditions; keep the full suite manifest for later resume")
    _inputs(suite)
    suite.set_defaults(handler=_suite)
    prepare = commands.add_parser("prepare", help="Download a versioned reasoning benchmark and its inputs")
    prepare.add_argument("benchmark", choices=("mindcube", "saw", "aime2025", "aime2026"))
    prepare.add_argument("--output", type=Path)
    prepare.add_argument("--limit", type=int)
    prepare.add_argument("--split", choices=("tiny", "full"), default="tiny")
    prepare.add_argument("--frames", type=int, default=32)
    prepare.set_defaults(handler=_prepare)
    scoring = commands.add_parser("evaluate", help="Evaluate a saved run; dry runs never report accuracy")
    scoring.add_argument("run", type=Path)
    scoring.set_defaults(handler=_evaluate)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return asyncio.run(args.handler(args)) if args.command in ("run", "suite") else args.handler(args)
    except KeyboardInterrupt:
        print("Interrupted. Completed tasks are saved; use the same command with --resume.", file=sys.stderr)
        return 130
    except (OSError, ValueError, KeyError, TypeError, ModelError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
