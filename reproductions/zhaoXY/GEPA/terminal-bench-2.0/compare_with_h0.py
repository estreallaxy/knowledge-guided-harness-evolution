#!/usr/bin/env python3
"""Per-task comparison of this unit's final evaluation against the H0 unit's.

Both summaries come from the same `summarize.py` shape and the same protocol
(train 30 tasks x 2 attempts), so the only variable is the instruction prompt.

Usage:
  python3 compare_with_h0.py \
      [--gepa results/summary.json] \
      [--h0 ../../H0/terminal-bench-2.0/results/summary.json] \
      [--out results/comparison.md]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parent
DEFAULT_GEPA = UNIT / "results" / "summary.json"
DEFAULT_H0 = UNIT.parents[1] / "H0" / "terminal-bench-2.0" / "results" / "summary.json"
DEFAULT_OUT = UNIT / "results" / "comparison.md"


def load(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing summary: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gepa", type=Path, default=DEFAULT_GEPA)
    parser.add_argument("--h0", type=Path, default=DEFAULT_H0)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    gepa, h0 = load(args.gepa), load(args.h0)
    gepa_rows = {row["task"]: row for row in gepa["per_task"]}
    h0_rows = {row["task"]: row for row in h0["per_task"]}
    tasks = sorted(set(gepa_rows) | set(h0_rows))

    lines = [
        "# GEPA × TB2 终评 vs H0 × TB2（逐题对照）",
        "",
        f"- GEPA 运行：`{gepa['run_id']}`（{gepa['n_tasks']} 题，pass@{gepa['attempts_per_task']}）",
        f"- H0 运行：`{h0['run_id']}`（{h0['n_tasks']} 题，pass@{h0['attempts_per_task']}）",
        "",
        "| 口径 | GEPA | H0 | Δ |",
        "| --- | --- | --- | --- |",
    ]

    def fmt(value, digits=4):
        return "n/a" if value is None else f"{value:.{digits}f}"

    d_pass = None
    if gepa.get("pass_at_k") is not None and h0.get("pass_at_k") is not None:
        d_pass = gepa["pass_at_k"] - h0["pass_at_k"]
    d_micro = None
    if gepa.get("trial_level_micro_pass_rate") is not None and h0.get("trial_level_micro_pass_rate") is not None:
        d_micro = gepa["trial_level_micro_pass_rate"] - h0["trial_level_micro_pass_rate"]
    lines += [
        f"| 任务级 pass@2 | {fmt(gepa.get('pass_at_k'))} ({gepa['successes']}/{gepa['n_tasks']}) "
        f"| {fmt(h0.get('pass_at_k'))} ({h0['successes']}/{h0['n_tasks']}) "
        f"| {('%+.4f' % d_pass) if d_pass is not None else 'n/a'} |",
        f"| trial-level micro | {fmt(gepa.get('trial_level_micro_pass_rate'))} "
        f"| {fmt(h0.get('trial_level_micro_pass_rate'))} "
        f"| {('%+.4f' % d_micro) if d_micro is not None else 'n/a'} |",
        f"| 成本 $ | {gepa.get('cost_usd')} | {h0.get('cost_usd')} | — |",
        "",
        "> 噪声底线（H0 单元 §4）：同配置重跑任务级 pass@2 浮动 ±3 题（0.63~0.73）。"
        "小于该幅度的差异不构成结论。",
        "",
        "## 逐题",
        "",
        "| task | GEPA | H0 | Δ | 备注 |",
        "| --- | --- | --- | --- | --- |",
    ]
    flips_up, flips_down, same = [], [], 0
    for task in tasks:
        g = gepa_rows.get(task, {})
        h = h0_rows.get(task, {})
        gs, hs = g.get("score"), h.get("score")
        if gs is None or hs is None:
            delta, note = "n/a", "有一侧未判分"
        else:
            delta = f"{gs - hs:+.1f}"
            if gs > hs:
                flips_up.append(task)
            elif gs < hs:
                flips_down.append(task)
            else:
                same += 1
            notes = []
            if g.get("exceptions"):
                notes.append("GEPA: " + "/".join(x for x in g["exceptions"] if x))
            if h.get("exceptions"):
                notes.append("H0: " + "/".join(x for x in h["exceptions"] if x))
            note = "；".join(notes) or "—"
        lines.append(
            f"| {task} | {'null' if gs is None else f'{gs:.1f}'} "
            f"| {'null' if hs is None else f'{hs:.1f}'} | {delta} | {note} |"
        )

    lines += [
        "",
        "## 汇总",
        "",
        f"- 翻转向上（GEPA 更好）：{len(flips_up)} 题 {flips_up if flips_up else ''}",
        f"- 翻转向下（GEPA 更差）：{len(flips_down)} 题 {flips_down if flips_down else ''}",
        f"- 持平：{same} 题",
        "",
    ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:14]))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
