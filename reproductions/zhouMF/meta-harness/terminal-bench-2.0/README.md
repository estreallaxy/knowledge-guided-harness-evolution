# Meta-Harness × Terminal-Bench 2.0 复现交付（周梦凡 / zhouMF）

在隔离的个人工作区里，用固定执行/优化模型 `deepseek/deepseek-v4-flash` 跑通 Meta-Harness 的
H0 基线与 trace 驱动的优化循环，只使用 `tb2-split-v1` 的 train 划分（30 题）。
所有原始产物留在本地，仓库只保存可审计的摘要与说明。

| 对象 | 通过 | 零分 | 未评分 | 任务数 | 尝试 | 摘要 |
| --- | --- | --- | --- | --- | --- | --- |
| H0 初始 harness（`baseline_kira`） | 38 | 17 | 5 | 30 | 60（2 trials） | [H0 摘要](results/h0/summary.json) |
| 候选 `enforced_final_state_audit`（前沿） | 20 | 8 | 2 | 30 | 30 | [候选摘要](results/p6/summary.json) |
| 候选 `deadline_audited_delivery` | 19 | 9 | 2 | 30 | 30 | [候选摘要](results/p6/summary.json) |
| 候选 `deadline_aware_delivery` | 18 | 9 | 3 | 30 | 30 | [候选摘要](results/p6/summary.json) |

H0 有三种口径，不可互相替代：计分均分 **0.6909**（38/55，只统计有 reward 的 trial）、
全 trial 均分 **0.6333**（38/60，未评分 trial 按 0 计入分母）、30 题 macro 任务均分
**0.6667**（20.0/30，先在任务内取均值再对任务取平均）。同口径复核（只保留候选与 H0
都计分的题）后，前沿候选 `enforced_final_state_audit`（28 题计分均分 0.7143 / 全 trial 0.6667）
净增益 **+3.6pt**，另两个候选为 0.0pt 与 −3.7pt。**该差异落在单题噪声范围内，不能定性为提升**；
两侧 trial 数不一致（候选 1 / 基线 2）是尚未解决的口径问题。

三种口径的重算脚本与输出见 [`code-adaptation/scripts/compute_scores.py`](code-adaptation/scripts/compute_scores.py)；
机读字段为 `results/*.json` 的 `mean_reward_scored`、`mean_reward_all_trials_zero_filled`、
`macro_task_mean`。

## 目录

| 路径 | 内容 |
| --- | --- |
| `configs/` | 三份配置：benchmark、H0、优化循环字段约定 |
| `code-adaptation/` | 上游适配补丁、运行脚本、P6 候选 harness 与提示模板 |
| `notes/` | 步骤清单、规划历史、适配记录、运行记录、总结 |
| `results/` | 可入库的结果摘要（`summary.json`） |
| `../code/` | 共享的 Meta-Harness 上游副本（保持与参考实现一致） |

## 环境准备

```bash
export BASE=/data1/users/zhouMF/knowledge-guided-harness-evolution/reproductions/zhouMF/meta-harness
export RD=$BASE/code/reference_examples/terminal_bench_2
export WS=$BASE/terminal-bench-2.0

curl -LsSf https://astral.sh/uv/install.sh | sh && source "$HOME/.local/bin/env"
cd "$RD"
patch --dry-run -p1 < "$WS/code-adaptation/upstream-adaptation.diff"
patch -p1 < "$WS/code-adaptation/upstream-adaptation.diff"   # 对干净上游副本执行一次
uv sync
bash "$WS/code-adaptation/scripts/p1_env_check.sh"      # 环境报告 → notes/p1-env-report.txt
```

需要可访问的 Docker 与网络；`uv sync` 使用 `code-adaptation/upstream-adaptation.diff`
描述的适配（见 [`code-adaptation/README.md`](code-adaptation/README.md)）。凭据只放本地
`.env`，不入库（模板见 `../code/.env.example`）。

## 运行入口

```bash
# H0 基线（单题 smoke / train 全量）
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train \
  bash "$WS/code-adaptation/scripts/run_local_docker.sh" agents.baseline_kira:AgentHarness full 1 1 -i bn-fit-modify

# 优化循环（提议器 = Claude Code CLI → 本地网关 → deepseek）
bash "$WS/code-adaptation/scripts/claude_deepseek_gateway.sh" start
bash "$WS/code-adaptation/scripts/run_meta_harness.sh" p6-main --iterations 2 --trials 1 --skip-baseline --concurrent 8

# 把 job 结果转成可入库摘要
python3 "$WS/code-adaptation/scripts/export_results.py" --jobs-dir "$RD/jobs" --out "$WS/results"
```

任务集 `tb2-split-v1`（train 30 / dev 19 / test 40）由 `benchmarks/terminal-bench-2.0/` 只读派生；
评测只用 train，dev/test 未运行。

## 验证与证据范围

```bash
cd "$RD" && uv run --with pytest --no-sync pytest tests/ -q     # 12/12 免 provider 单测
python3 ../../../../knowledge/source-packets/verify_zhoumf.py        # 来源包结构/锚点/凭据
```

来源包校验覆盖本人 5 个 `SourcePacket`（结构、论文分页锚点、代码行号锚点、凭据泄漏），
与上游执行无关。逐次运行条件、逐题 reward、token、费用与墙钟见
[`notes/run-log.md`](notes/run-log.md)；偏差与待办见
[`notes/reproduction-summary.md`](notes/reproduction-summary.md)。

已知边界：DeepSeek 余额（¥2.26）不足以把候选补到 2 trials 或扩到论文默认 5 轮；
与其余成员的交叉核对因工作区私有未完成。原始 `jobs/`、`logs/`、`runs/` 不入库。
