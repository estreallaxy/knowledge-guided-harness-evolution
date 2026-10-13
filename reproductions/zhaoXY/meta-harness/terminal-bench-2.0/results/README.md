# Result summary

大体积原始产物留在本地 `runs/`（`.gitignore` 已挡）；本文件只登记可交叉核对的摘要字段。

## 1. H0 baseline（2026-10-08）

| Field | Value |
| --- | --- |
| Baseline | H0 = `code/reference_examples/terminal_bench_2/agents/baseline_kira.py`（Terminus2/Kira track，逐字节未改动） |
| Benchmark | Terminal-Bench 2.0（仓库冻结快照 `benchmarks/terminal-bench-2.0/dataset`） |
| Code revision | `4aaa62901c105e112a576bbb35cb1d64ee9d0a21` |
| H0 revision | Meta-Harness upstream `8123ccabe2b19fa1123090b2e5f1bacc20963ce8`；H0 与 prompt 未作本地修改 |
| Dataset split | `tb2-split-v1` train（30 题 × 2 次 = 60 trial） |
| Model and provider | `deepseek/deepseek-v4-flash`（api.deepseek.com；litellm 原生 deepseek 路由） |
| Random seed | 无（harbor 未暴露 seed；同条件重复 2 次） |
| Score | trial-level micro pass rate：**40/60 = 66.7%** |
| Successful / failed / ungraded | 40 / 20 / 0（失败构成：`AgentTimeoutError` 10、真答错 7、`VerifierTimeoutError` 3） |
| Tokens / calls / cost / elapsed time | 281.8M in / 6.04M out · **$10.13** · 113 分钟（并发 10；宿主 load 90~105） |
| Config path | `terminal-bench-2.0/configs/terminal-bench-2.0.yaml` |
| Trace path | `runs/jobs/h0-train-baseline/`（本地） |
| Notes | 交叉核对须知（VerifierTimeout 计分口径、并发偏离）见 `terminal-bench-2.0/notes/README.md` 第三节 |

## 2. Meta-Harness 首轮 + 定向复验（2026-10-09 / 10-11）

| Field | Value |
| --- | --- |
| Baseline | 同上 H0；Phase 0 同批新跑 `baseline_terminus2` = 61.7%（$6.97） |
| Benchmark | Terminal-Bench 2.0，`tb2-split-v1` train（30 题 × 2 次 = 60 trial） |
| Code revision | `4aaa629…`；优化器为 `litellm_proposer.py`（进程内 litellm 直调） |
| H0 revision | 与第 1 节相同，未改动 |
| Dataset split | 同上 |
| Model and provider | 执行与优化模型均为 `deepseek/deepseek-v4-flash` |
| Random seed | 无 |
| Score | trial-level micro pass rate：首轮候选 `kira_context_budget` **39/60 = 65.0%**（H0 40/60 = 66.7%、terminus2 37/60 = 61.7%；相对「两基线逐题最优」41/60 = 68.3% 为 **−3.3pp**） |
| Successful / failed / ungraded | 39 / 21 / 0（`AgentTimeoutError` 10、`VerifierTimeoutError` 3、`BlockError` 2[基础设施]、其余真答错 6） |
| Tokens / calls / cost / elapsed time | 候选评估 $11.36 + 优化器 $0.17（539s）· 墙钟 219 分钟 |
| Config path | `terminal-bench-2.0/configs/meta-harness.yaml` |
| Trace path | `runs/jobs/evolve-1/`、`runs/logs/evolve-1/`、`runs/jobs/confirm5-*/`（本地） |
| Notes | **定向复验（confirm5：4 题 × 5 次 × 两臂，$12.01）判定「该机制对本环境无影响，−3.3pp 是 n=2 噪声」**；gcode / raman 的超时为任务固有（低负载下依旧）。逐题对照见 `terminal-bench-2.0/notes/README.md` 第四节 |

**成本台账（Meta-Harness 相关，单独记账）**：优化器 $0.17 + 候选 smoke $0.02 + 首轮候选评估 $11.36 + confirm5 复验 $12.01 ≈ **$23.56**（terminus2 基线 $6.97 属 Phase 0 执行侧，另计）。
