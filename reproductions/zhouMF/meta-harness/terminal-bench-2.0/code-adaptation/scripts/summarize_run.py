#!/usr/bin/env python3
"""把 Harbor job 目录汇总成可提交的记录（周梦凡个人工具，不属于 code/ 上游副本）。

运行产物（jobs/、runs/、logs/）都在 .gitignore 里，不会入库，所以每个 job 的关键指标
必须转写到 notes/ 才能追溯。本脚本负责这一步，字段与 configs/meta-harness.yaml 的
records.fields 对齐。

用法：
    python3 code-adaptation/scripts/summarize_run.py <job_dir> [<job_dir> ...]
    python3 code-adaptation/scripts/summarize_run.py <job_dir> --append-to notes/run-log.md
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


def summarize(job_dir: Path) -> str:
    job = load(job_dir / "result.json")
    trials = []
    for trial in sorted(job_dir.iterdir()):
        if not trial.is_dir() or not (trial / "result.json").is_file():
            continue
        trials.append(load(trial / "result.json"))
    if not trials:
        raise SystemExit(f"{job_dir}: 没有找到 trial 级 result.json")

    first = trials[0]
    config = first["config"]
    agent = config["agent"]
    model = agent["model_name"]
    env = config["environment"]["type"]
    task_source = config["task"]["path"] or config["task"].get("git_url") or "?"

    # 并发数只在 job 级 config.json 里，trial 级配置不带
    job_config_path = job_dir / "config.json"
    job_config = load(job_config_path) if job_config_path.is_file() else {}
    n_concurrent = (agent.get("n_concurrent")
                    or job_config.get("n_concurrent_trials")
                    or job_config.get("n_concurrent"))
    # job 级 config.json 不记 --n-attempts，用实际 trial 数/任务数还原
    per_task: dict[str, int] = {}
    for trial in trials:
        name = trial.get("task_name") or "?"
        per_task[name] = per_task.get(name, 0) + 1
    attempts = max(per_task.values()) if per_task else None

    stats = job.get("stats", {})
    lines = []
    lines.append(f"### {job_dir.name}")
    lines.append("")
    lines.append(f"- 实验条件：agent=`{agent['name']}`，model=`{model}`，environment=`{env}`，"
                 f"n_concurrent={n_concurrent if n_concurrent is not None else '未记录'}，"
                 f"trials/任务={attempts if attempts is not None else '未记录'}，"
                 f"任务数={len(per_task)}")
    lines.append(f"- 任务来源：`{task_source}`（source={config['task'].get('source')}）")
    lines.append(f"- 时间：{job.get('started_at')} → {job.get('finished_at')}")
    lines.append(f"- 汇总：trials={job.get('n_total_trials')}，完成={stats.get('n_completed_trials')}，"
                 f"异常={stats.get('n_errored_trials')}，重试={stats.get('n_retries')}")
    if stats.get("n_input_tokens") is not None:
        lines.append(f"- 合计用量：input_tokens={stats.get('n_input_tokens')}，"
                     f"cache_tokens={stats.get('n_cache_tokens')}，"
                     f"output_tokens={stats.get('n_output_tokens')}，"
                     f"cost_usd={stats.get('cost_usd'):.6f}")
    lines.append("")
    lines.append("| # | task | trial | reward | in_tok | out_tok | cost_usd | wall_s | exception |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for i, t in enumerate(trials, 1):
        ar = t.get("agent_result") or {}
        rewards = (t.get("verifier_result") or {}).get("rewards") or {}
        reward = rewards.get("reward")
        exc = t.get("exception_info")
        exc_txt = "无" if not exc else f"{(exc.get('type') or 'error')}"
        lines.append(
            f"| {i} | {t.get('task_name')} | {t.get('trial_name')} "
            f"| {'—' if reward is None else round(float(reward), 4)} "
            f"| {ar.get('n_input_tokens', '—')} | {ar.get('n_output_tokens', '—')} "
            f"| {'—' if ar.get('cost_usd') is None else format(ar['cost_usd'], '.6f')} "
            f"| {seconds_between(t.get('started_at'), t.get('finished_at'))} "
            f"| {exc_txt} |"
        )
    rewards_all = [
        float((t.get("verifier_result") or {}).get("rewards", {}).get("reward"))
        for t in trials
        if (t.get("verifier_result") or {}).get("rewards", {}).get("reward") is not None
    ]
    if rewards_all:
        lines.append("")
        lines.append(f"- 平均 reward：{sum(rewards_all) / len(rewards_all):.4f}"
                     f"（{sum(1 for r in rewards_all if r >= 1.0)}/{len(rewards_all)} 满分）")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("job_dirs", nargs="+", type=Path)
    ap.add_argument("--append-to", type=Path, default=None,
                    help="追加写入该 markdown 文件，而不是只打印")
    args = ap.parse_args()

    blocks = [summarize(d) for d in args.job_dirs]
    text = "\n".join(blocks)
    print(text, end="")
    if args.append_to:
        with args.append_to.open("a", encoding="utf-8") as handle:
            handle.write("\n" + text)
        print(f"\n[已追加到 {args.append_to}]", flush=True)


if __name__ == "__main__":
    main()
