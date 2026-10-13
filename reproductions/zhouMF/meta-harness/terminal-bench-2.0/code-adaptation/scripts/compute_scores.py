#!/usr/bin/env python3
"""从已入库的 results/*.json 重算三种分数口径（不依赖本地 jobs/ 产物）。

口径定义（互不替代，写结论时必须写明用哪一种）：
  * scored             只统计有 reward 的 trial：successes / scored_trials
  * all-trials zero-fill  未评分 trial 按 0 计入分母：successes / total_trials
  * macro task mean    先在任务内对有 reward 的 trial 取均值，再对任务取算术平均
用法（在 reproductions/zhouMF/meta-harness/terminal-bench-2.0 下执行）：
    python3 code-adaptation/scripts/compute_scores.py [--results results]
存储值与重算值不一致时以非零退出码报错。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


MISMATCH = 0


def rerun(summary: dict) -> dict:
    rows = summary["per_task"]
    scored = [r for row in rows for r in row["rewards"] if r is not None]
    ungraded = sum(1 for row in rows for r in row["rewards"] if r is None)
    total = summary.get("total_trials") or (len(scored) + ungraded)
    successes = sum(1 for r in scored if r >= 1.0)
    macro = [row["mean"] for row in rows if row["mean"] is not None]
    return {
        "task_count": len(rows),
        "total_trials": total,
        "scored_trials": len(scored),
        "ungraded_trials": ungraded,
        "successes": successes,
        "zero_reward": len(scored) - successes,
        "scored": round(successes / len(scored), 4) if scored else None,
        "all_trials_zero_filled": round(successes / total, 4) if total else None,
        "macro_task_mean": round(sum(macro) / len(macro), 4) if macro else None,
        "macro_sum": round(sum(macro), 4),
        "macro_task_count": len(macro),
    }


def line(name: str, calc: dict, stored: dict) -> list[str]:
    checks = [("scored", calc["scored"], stored.get("mean_reward_scored")),
              ("all-trials zero-fill", calc["all_trials_zero_filled"],
               stored.get("mean_reward_all_trials_zero_filled")),
              ("macro task mean", calc["macro_task_mean"], stored.get("macro_task_mean"))]
    out = [f"{name}: tasks={calc['task_count']} trials={calc['total_trials']} "
           f"scored={calc['scored_trials']} succ={calc['successes']} "
           f"zero={calc['zero_reward']} ungraded={calc['ungraded_trials']}"]
    out.append(f"    scored               = {calc['successes']}/{calc['scored_trials']} "
               f"= {calc['scored']}   (stored {stored.get('mean_reward_scored')})")
    out.append(f"    all-trials zero-fill = {calc['successes']}/{calc['total_trials']} "
               f"= {calc['all_trials_zero_filled']}   "
               f"(stored {stored.get('mean_reward_all_trials_zero_filled')})")
    out.append(f"    macro task mean      = {calc['macro_sum']}/{calc['macro_task_count']} "
               f"= {calc['macro_task_mean']}   (stored {stored.get('macro_task_mean')})")
    for label, a, b in checks:
        if a != b:
            MISMATCH += 1
            out.append(f"    !! 不一致：{label} 重算 {a} != 存储 {b}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", type=Path, default=Path("results"))
    args = ap.parse_args()
    h0 = json.loads((args.results / "h0" / "summary.json").read_text(encoding="utf-8"))
    p6 = json.loads((args.results / "p6" / "summary.json").read_text(encoding="utf-8"))
    cands = p6["candidates"]

    out = ["== 三种口径（由 results/*.json 的逐题 rewards 重算） =="]
    out += line(f"H0 {h0['job']}", rerun(h0), h0)
    for name, cand in cands.items():
        out += line(f"候选 {name}", rerun(cand), cand)

    out.append("")
    out.append("== 同口径对比（只保留候选与 H0 都计分的任务）==")
    h0_map = {row["task"]: row["mean"] for row in h0["per_task"] if row["mean"] is not None}
    for name, cand in cands.items():
        cand_map = {row["task"]: row["mean"] for row in cand["per_task"]
                    if row["mean"] is not None}
        common = sorted(set(h0_map) & set(cand_map))
        base = sum(h0_map[t] for t in common) / len(common)
        cm = sum(cand_map[t] for t in common) / len(common)
        out.append(f"{name}: 共同任务 {len(common)} | H0 {base:.4f} vs 候选 {cm:.4f} "
                   f"| 净差 {(cm - base) * 100:+.1f}pt "
                   f"| 升 {sum(1 for t in common if cand_map[t] > h0_map[t])} / "
                   f"降 {sum(1 for t in common if cand_map[t] < h0_map[t])}")
    print("\n".join(out))
    print(f"\n不一致项: {MISMATCH}")
    return 1 if MISMATCH else 0


if __name__ == "__main__":
    raise SystemExit(main())
