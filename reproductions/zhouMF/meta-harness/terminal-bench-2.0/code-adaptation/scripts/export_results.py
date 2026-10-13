#!/usr/bin/env python3
"""把 Harbor job 目录导出成可提交的 results/*.json 摘要（周梦凡个人工具）。

原始产物 jobs/、logs/ 在 .gitignore 内不入库，因此关键指标必须转写进 results/。
用法：
    python3 export_results.py --jobs-dir <jobs_dir> --out <results_dir> \
        --h0-job h0-baseline-r2 --candidate-job p6-main
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def seconds_between(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    parse = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    return round((parse(end) - parse(start)).total_seconds(), 1)


def summarize_job(job_dir: Path) -> dict:
    job = load(job_dir / "result.json")
    trials = [load(t / "result.json") for t in sorted(job_dir.iterdir())
              if t.is_dir() and (t / "result.json").is_file()]
    first = trials[0]
    config = first["config"]
    per_task: dict[str, list] = {}
    exceptions: dict[str, int] = {}
    for trial in trials:
        rewards = (trial.get("verifier_result") or {}).get("rewards") or {}
        reward = rewards.get("reward")
        per_task.setdefault(trial.get("task_name") or "?", []).append(
            None if reward is None else float(reward))
        exc = trial.get("exception_info")
        if exc:
            key = exc.get("type") or "error"
            exceptions[key] = exceptions.get(key, 0) + 1
    scored = [r for values in per_task.values() for r in values if r is not None]
    stats = job.get("stats", {})
    return {
        "job": job_dir.name,
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
        "wall_seconds": seconds_between(job.get("started_at"), job.get("finished_at")),
        "agent": config["agent"]["name"],
        "model": config["agent"]["model_name"],
        "environment": config["environment"]["type"],
        "task_source": config["task"].get("path") or config["task"].get("git_url") or "?",
        "task_count": len(per_task),
        "total_trials": job.get("n_total_trials"),
        "scored_trials": len(scored),
        "ungraded_trials": sum(1 for v in per_task.values() for r in v if r is None),
        "successes": sum(1 for r in scored if r >= 1.0),
        "zero_reward": sum(1 for r in scored if r < 1.0),
        "mean_reward_scored": round(sum(scored) / len(scored), 4) if scored else None,
        "exceptions": exceptions,
        "tokens": {k: stats.get(k) for k in
                   ("n_input_tokens", "n_cache_tokens", "n_output_tokens")},
        "cost_usd_from_agent_result": round(sum(
            (t.get("agent_result") or {}).get("cost_usd") or 0 for t in trials), 6),
        "per_task": [
            {"task": task, "trials": len(values),
             "rewards": values,
             "mean": round(sum(r for r in values if r is not None)
                           / max(1, len([r for r in values if r is not None])), 4)
             if any(r is not None for r in values) else None}
            for task, values in sorted(per_task.items())
        ],
    }


def same_basis(h0: dict, candidate: dict) -> dict:
    """只保留两侧都有计分 trial 的任务，做同口径比较。"""
    def scored_map(summary):
        return {row["task"]: row["mean"] for row in summary["per_task"]
                if row["mean"] is not None}
    base, cand = scored_map(h0), scored_map(candidate)
    common = sorted(set(base) & set(cand))
    base_mean = round(sum(base[t] for t in common) / len(common), 4) if common else None
    cand_mean = round(sum(cand[t] for t in common) / len(common), 4) if common else None
    return {
        "common_tasks": len(common),
        "h0_mean": base_mean,
        "candidate_mean": cand_mean,
        "delta_pt": None if base_mean is None else round((cand_mean - base_mean) * 100, 1),
        "up": [t for t in common if cand[t] > base[t]],
        "down": [t for t in common if cand[t] < base[t]],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--h0-job", default="h0-baseline-r2")
    ap.add_argument("--candidate-job", default="p6-main")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "h0").mkdir(parents=True, exist_ok=True)
    (args.out / "p6").mkdir(parents=True, exist_ok=True)

    h0 = summarize_job(args.jobs_dir / args.h0_job)
    (args.out / "h0" / "summary.json").write_text(
        json.dumps(h0, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    p6_dir = args.jobs_dir / args.candidate_job
    candidates = {}
    for child in sorted(p6_dir.iterdir()):
        if child.is_dir() and child.name.startswith("evolve-") and (child / "result.json").is_file():
            candidates[child.name.removeprefix("evolve-").removesuffix("-t1")] = summarize_job(child)
    (args.out / "p6" / "summary.json").write_text(
        json.dumps({"candidates": candidates}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    overall = {
        "schema_version": 1,
        "baseline": "meta-harness",
        "benchmark": "terminal-bench-2.0",
        "harness": {"h0": "baseline_kira", "candidates": sorted(candidates)},
        "model_protocol": "deepseek/deepseek-v4-flash（执行与优化共用）",
        "task_split": "train（30 题；dev 19 / test 40 未运行）",
        "h0": h0,
        "candidates": candidates,
        "same_basis_vs_h0": {name: same_basis(h0, cand) for name, cand in candidates.items()},
        "frontier": max(candidates, key=lambda name: candidates[name]["mean_reward_scored"])
        if candidates else None,
        "notes": [
            "H0 为 30 题 × 2 trial；候选为 30 题 × 1 trial，两侧分母不一致，已用 same_basis_vs_h0 只保留共同计分任务。",
            "未计分 trial（异常/超时）计入 ungraded_trials，不计入 mean_reward_scored。",
            "原始产物 jobs/ 与 logs/ 保留在个人工作区，未入库。",
        ],
    }
    (args.out / "summary.json").write_text(
        json.dumps(overall, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"h0": {k: h0[k] for k in ('task_count', 'total_trials', 'scored_trials',
                                                'mean_reward_scored')},
                      "candidates": {n: {k: c[k] for k in ('task_count', 'scored_trials',
                                                           'mean_reward_scored')}
                                     for n, c in candidates.items()},
                      "frontier": overall["frontier"],
                      "same_basis": overall["same_basis_vs_h0"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
