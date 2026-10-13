#!/usr/bin/env python3
"""Summarize an H0 × Terminal-Bench 2.0 job into results/summary.{json,md}.

Reads every trial result.json under runs/jobs/<run-id>/ and writes the
committable summary (raw job directories stay local, covered by .gitignore).

Scoring (recorded in the generated report):
  - One task = one row; its score is the best reward across its attempts
    (pass@k, k = attempts per task).
  - success: best reward == 1.0. failed: best reward == 0.0. ungraded: no
    attempt produced a verifier verdict (e.g. verifier timeout).
  - The denominator is the number of tasks; ungraded tasks count in the
    denominator but not in avg_score.

Usage:
  python3 summarize.py [--job-dir runs/jobs/<run-id>] [--out-dir results]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

UNIT = Path(__file__).resolve().parent
RUNS = UNIT / "runs"
JOBS = RUNS / "jobs"


def newest_job_dir() -> Path:
    candidates = [p for p in JOBS.iterdir() if p.is_dir()] if JOBS.is_dir() else []
    if not candidates:
        raise SystemExit(f"no job directories under {JOBS}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_trials(job_dir: Path) -> list[dict]:
    trials = []
    for trial_dir in sorted(p for p in job_dir.iterdir() if p.is_dir()):
        result_file = trial_dir / "result.json"
        if not result_file.is_file():
            continue
        data = json.loads(result_file.read_text(encoding="utf-8"))
        rewards = (data.get("verifier_result") or {}).get("rewards") or {}
        agent_result = data.get("agent_result") or {}
        exception = data.get("exception_info") or {}
        started, finished = data.get("started_at"), data.get("finished_at")
        wall = None
        if started and finished:
            wall = (
                datetime.fromisoformat(finished.replace("Z", "+00:00"))
                - datetime.fromisoformat(started.replace("Z", "+00:00"))
            ).total_seconds()
        trials.append(
            {
                "trial": data.get("trial_name", trial_dir.name),
                "task": data.get("task_name", trial_dir.name.split("__")[0]),
                "reward": rewards.get("reward"),
                "exception": exception.get("exception_type"),
                "input_tokens": agent_result.get("n_input_tokens"),
                "cache_tokens": agent_result.get("n_cache_tokens"),
                "output_tokens": agent_result.get("n_output_tokens"),
                "cost_usd": agent_result.get("cost_usd"),
                "wall_s": wall,
            }
        )
    return trials


def per_task(trials: list[dict]) -> list[dict]:
    tasks: dict[str, list[dict]] = {}
    for t in trials:
        tasks.setdefault(t["task"], []).append(t)
    rows = []
    for task, attempts in sorted(tasks.items()):
        graded = [a["reward"] for a in attempts if a["reward"] is not None]
        best = max(graded) if graded else None
        status = "ungraded" if best is None else ("success" if best == 1.0 else "failed")
        rows.append(
            {
                "task": task,
                "attempts": len(attempts),
                "score": best,
                "status": status,
                "exceptions": [a["exception"] for a in attempts if a["exception"]],
                "cost_usd": round(sum(a["cost_usd"] or 0.0 for a in attempts), 4),
                "wall_s": int(max((a["wall_s"] or 0.0) for a in attempts)),
            }
        )
    return rows


def build(job_dir: Path) -> dict:
    trials = load_trials(job_dir)
    rows = per_task(trials)
    job = json.loads((job_dir / "result.json").read_text(encoding="utf-8"))
    stats = job.get("stats", {})

    successes = sum(r["status"] == "success" for r in rows)
    failed = sum(r["status"] == "failed" for r in rows)
    ungraded = sum(r["status"] == "ungraded" for r in rows)
    graded = [r["score"] for r in rows if r["score"] is not None]

    elapsed_s = None
    if job.get("started_at") and job.get("finished_at"):
        elapsed_s = (
            datetime.fromisoformat(job["finished_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
        ).total_seconds()

    return {
        "run_id": job_dir.name,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "job_dir": str(job_dir),
        "n_tasks": len(rows),
        "trials_total": len(trials),
        "trials_passed": sum(1 for t in trials if t["reward"] == 1.0),
        "trial_level_micro_pass_rate": (
            round(sum(1 for t in trials if t["reward"] == 1.0) / len(trials), 4)
            if trials
            else None
        ),
        "trials_completed": stats.get("n_completed_trials"),
        "trials_errored": stats.get("n_errored_trials"),
        "trials_cancelled": stats.get("n_cancelled_trials"),
        "trials_retried": stats.get("n_retries"),
        "pass_at_k": round(successes / len(rows), 4) if rows else None,
        "attempts_per_task": max((r["attempts"] for r in rows), default=None),
        "successes": successes,
        "failed": failed,
        "ungraded": ungraded,
        "avg_score_graded": round(sum(graded) / len(graded), 4) if graded else None,
        "cost_usd": round(stats.get("cost_usd") or 0.0, 4),
        "elapsed_s": int(elapsed_s) if elapsed_s is not None else None,
        "input_tokens": stats.get("n_input_tokens"),
        "cache_tokens": stats.get("n_cache_tokens"),
        "output_tokens": stats.get("n_output_tokens"),
        "trial_exception_breakdown": dict(
            Counter(t["exception"] for t in trials if t["exception"])
        ),
        "job_started_at": job.get("started_at"),
        "job_finished_at": job.get("finished_at"),
        "per_task": rows,
    }


def render_md(s: dict) -> str:
    rows = s["per_task"]
    lines = [
        "# Result summary — H0 × Terminal-Bench 2.0",
        "",
        "由 `summarize.py` 从本地 job 目录生成（原始产物不入库）。",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Baseline | H0 = `terminus-kira`（`agents.baseline_kira:AgentHarness`，本单元 `code/terminus-kira/baseline_kira.py`，sha256 `e06b9273…`） |",
        "| Benchmark | Terminal-Bench 2.0（仓库冻结快照，本地 Docker 后端） |",
        f"| Dataset split | train（{s['n_tasks']} 题，`benchmarks/terminal-bench-2.0/split-v1.json`） |",
        "| Model | `deepseek/deepseek-v4-flash`（API 实际标识 `deepseek-flash`，2026-10-13 核实），temperature 0.7 |",
        f"| Run id | `{s['run_id']}`（{s['job_started_at']} → {s['job_finished_at']}） |",
        f"| **Score** | **pass@{s['attempts_per_task']} = {s['pass_at_k']}**（{s['successes']}/{s['n_tasks']}）"
        f"；avg_score（计入判分题）= {s['avg_score_graded']} |",
        f"| Successful / failed / ungraded | {s['successes']} / {s['failed']} / {s['ungraded']} |",
        f"| Trials | {s['trials_total']} 总数（完成 {s['trials_completed']}、出错 {s['trials_errored']}、重试 {s['trials_retried']}）"
        f"；trial-level micro pass rate = {s['trial_level_micro_pass_rate']}（{s['trials_passed']}/{s['trials_total']}） |",
        f"| Tokens / cost / elapsed | {s['input_tokens']} in（缓存 {s['cache_tokens']}）/ {s['output_tokens']} out · ${s['cost_usd']}"
        f" · {s['elapsed_s']} s（job 首启→最终结束的总跨度；若中途执行过 `harbor job resume`，该跨度含中断间隔，"
        f"实际计算墙钟见 `../notes/stage1-summary.md`） |",
        "| Config path | `configs/h0.yaml`（`command` 字段即实跑命令） |",
        f"| Trace path | 本地不入库：`runs/jobs/{s['run_id']}/<task>__<id>/agent/trajectory.json` |",
        "",
        "## 计算口径",
        "",
        f"- **pass@{s['attempts_per_task']}**：每题 {s['attempts_per_task']} 次 attempt，取最高分为该题得分；1.0 记 success。",
        f"- 分母固定为 {s['n_tasks']}（题数）；未判分题（无 verifier 终判）计入分母、不计入 avg_score。",
        "- 状态：success（最高分 1.0）/ failed（最高分 0.0）/ ungraded（无有效判分）。",
        f"- **trial-level micro pass rate**（trial 级通过率，与 main 上各线文档同一术语）= "
        f"{s['trials_passed']}/{s['trials_total']} = {s['trial_level_micro_pass_rate']}。",
        "- 两个口径不可互换：任务级 pass@k 衡量「该题是否解出」，trial 级对每次尝试平均。",
        "- tokens / cost 取 job `result.json` 的 stats；逐题明细见 `summary.json` 与本地 trial 目录。",
        "",
        f"## 逐题结果（run `{s['run_id']}`）",
        "",
        "| task | score | status | cost $ | wall s | exception |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        score = "null" if r["score"] is None else f"{r['score']:.1f}"
        exc = "；".join(x for x in r["exceptions"] if x) or "—"
        lines.append(
            f"| {r['task']} | {score} | {r['status']} | {r['cost_usd']:.3f} | {r['wall_s']} | {exc} |"
        )
    if s["trial_exception_breakdown"]:
        lines += [
            "",
            "## trial 级异常分布",
            "",
            "| exception_type | trials |",
            "| --- | --- |",
        ]
        for name, count in sorted(s["trial_exception_breakdown"].items(), key=lambda x: -x[1]):
            lines.append(f"| {name} | {count} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-dir", type=Path, default=None,
                        help="job directory (default: newest under runs/jobs/)")
    parser.add_argument("--out-dir", type=Path, default=UNIT / "results")
    args = parser.parse_args()

    job_dir = args.job_dir or newest_job_dir()
    if not (job_dir / "result.json").is_file():
        raise SystemExit(f"no result.json in {job_dir} (job still running?)")

    summary = build(job_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.out_dir / "summary.md").write_text(render_md(summary), encoding="utf-8")

    print(
        f"{summary['run_id']}: pass@{summary['attempts_per_task']} = {summary['pass_at_k']} "
        f"({summary['successes']}/{summary['n_tasks']}), "
        f"trial-level micro = {summary['trial_level_micro_pass_rate']} "
        f"({summary['trials_passed']}/{summary['trials_total']}), "
        f"{summary['failed']} failed / {summary['ungraded']} ungraded, "
        f"${summary['cost_usd']}, {summary['elapsed_s']}s"
    )
    print(f"wrote {args.out_dir/'summary.json'} and {args.out_dir/'summary.md'}")


if __name__ == "__main__":
    main()
