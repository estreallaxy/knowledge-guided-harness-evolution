| 实验 | 执行 Harness | 优化方法 | Benchmark | 状态 | 结果 |
| --- | --- | --- | --- | --- | --- |
| H0 + Terminal-Bench 2.0 | 每人 `code/reference_examples/terminal_bench_2/agents/baseline_kira.py` | 无 | [Terminal-Bench 2.0](../benchmarks/terminal-bench-2.0/README.md) | 待运行 | 分别保存在 `reproductions/<成员>/meta-harness/runs/` |
| Meta-Harness + Terminal-Bench 2.0 | 每人工作区内的 H0 | 每人 `code/reference_examples/terminal_bench_2/meta_harness.py` | [Terminal-Bench 2.0](../benchmarks/terminal-bench-2.0/README.md) | 待复现 | 分别保存在 `reproductions/<成员>/meta-harness/runs/` |

## 各成员运行记录

四人各自的原始产物保存在自己的 `reproductions/<成员>/meta-harness/runs/`（本地，不提交）。下表只登记可交叉核对的摘要字段；条件不一致的条目必须标出。

| 成员 | 实验 | 划分 | 模型 | 后端 | 并发 | 通过率 | 墙钟 | 费用 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zhaoXY | H0 + TB2 | train (30题×2次=60 trial) | `deepseek-v4-flash` | docker (本地) | 10 | **40/60 = 66.7%** | 113 分钟 | $10.13 | 已完成，见下 |
| zhouMF | H0 + TB2 | — | — | — | — | — | — | — | 待运行 |
| wangY | H0 + TB2 | — | — | — | — | — | — | — | 待运行 |
| liYK | H0 + TB2 | — | — | — | — | — | — | — | 待运行 |

### zhaoXY · H0 baseline（2026-10-08）

- **摘要**：`reproductions/zhaoXY/meta-harness/runs/h0-train-baseline-summary.json`
- **原始产物**：`reproductions/zhaoXY/meta-harness/runs/jobs/h0-train-baseline/`（被 `.gitignore` 忽略）
- **配置**：`reproductions/zhaoXY/meta-harness/configs/terminal-bench-2.0.yaml`
- **逐题结果**：18 题两次全过 / 4 题部分通过 / 8 题两次全败
- **失败构成（20 个 trial）**：`AgentTimeoutError` 10、**真答错** 7、**`VerifierTimeoutError` 3**

> **交叉核对须知**：`VerifierTimeoutError`（`query-optimize`×2、`torch-pipeline-parallelism`×1）**不是 agent 能力失败**，是验证器跑满 900s 被切断，属评测侧开销。直接计入通过率会低估 H0。四人需就这类 trial 的计分口径达成一致后重算。
>
> 并发 10 是**对共同协议的偏离**（协议默认 50）。原因是运行时宿主 load average 已达 82（64 核，另有他人 49 个容器）。10 个 `AgentTimeoutError` 中有多少是负载导致的假失败，需在低负载下复跑才能定量。
