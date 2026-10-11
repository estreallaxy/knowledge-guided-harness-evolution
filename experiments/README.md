| 实验 | 执行 Harness | 优化方法 | Benchmark | 状态 | 结果 |
| --- | --- | --- | --- | --- | --- |
| H0 + Terminal-Bench 2.0 | 每人 `code/reference_examples/terminal_bench_2/agents/baseline_kira.py` | 无 | [Terminal-Bench 2.0](../benchmarks/terminal-bench-2.0/README.md) | 进行中（zhaoXY 已完成，见下） | 分别保存在 `reproductions/<成员>/meta-harness/runs/` |
| Meta-Harness + Terminal-Bench 2.0 | 每人工作区内的 H0 | 每人 `code/reference_examples/terminal_bench_2/meta_harness.py` | [Terminal-Bench 2.0](../benchmarks/terminal-bench-2.0/README.md) | 进行中（zhaoXY 已完成首轮 + 定向复验，见下） | 分别保存在 `reproductions/<成员>/meta-harness/runs/` |

## 各成员运行记录

四人各自的原始产物保存在自己的 `reproductions/<成员>/meta-harness/runs/`（本地，不提交）。下表只登记可交叉核对的摘要字段；条件不一致的条目必须标出。

| 成员 | 实验 | 划分 | 模型 | 后端 | 并发 | 通过率 | 墙钟 | 费用 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zhaoXY | H0 + TB2 | train (30题×2次=60 trial) | `deepseek-v4-flash` | docker (本地) | 10 | **40/60 = 66.7%** | 113 分钟 | $10.13 | 已完成，见下 |
| zhaoXY | Meta-Harness + TB2 首轮 | train (30题×2次) | `deepseek-v4-flash` | docker (本地) | 10 | 候选 65.0%（H0 66.7%） | 219 分钟 | $11.36（执行）/ $0.17（优化器） | 首轮完成；定向复验判无显著差异，见下 |
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

### zhaoXY · Meta-Harness 首轮 + 定向复验（2026-10-09 / 10-11）

**首轮（`evolve-1`，2026-10-09 01:26–05:05）**

- 优化器（协议要求的 `deepseek-v4-flash`，`litellm_proposer.py` 进程内直调，$0.17）产出候选 `kira_context_budget`：每次 LLM 调用前把超 120k token 的最老终端观测压成「前 700 + 后 500 字符 + 省略说明」；未超预算时逐字节不变。
- 候选 smoke 1/1 通过；正式评估 30 题 × 2 = 60 trial → **65.0%**（同批 H0 66.7%、terminus2 61.7%），执行费用 $11.36。
- 逐题对比 H0 仅 3 题变化（`gcode-to-text` 0→0.5、`make-mips-interpreter` 0.5→0、`mcmc-sampling-stan` 1.0→0.5）；相对「两基线逐题最优」68.3% 为 **−3.3pp**。
- trace 诊断：压缩机制确实生效（长任务每步 prompt −12.4%），未发现候选代码 bug；2 例 `BlockError` 是 harbor/docker 基础设施卡死，非候选所致。

**定向复验（`confirm5`：4 题 × 5 次 × 两臂；10-09 跑 kira 臂 + 候选臂 14/20，10-11 低负载补跑剩余 6 个；合计 $12.01）**

| 题 | kira | 候选 | Δ |
| --- | --- | --- | --- |
| gcode-to-text | 0/5 | 0/5 | 0 |
| make-mips-interpreter | 0/5 | 0/4\* | 0 |
| mcmc-sampling-stan | 4/5 | 5/5 | +1 |
| raman-fitting | 1/5 | 0/5 | −1 |

\* 候选臂 5 个 trial 中 1 个以 harbor 侧 `ValueError: embedded null byte` 提前终止、未计分。

**结论（按 `runs/confirm5/run.sh` 事前写定的判定标准）**：三条判据均未触发——gcode 上候选并未显著高于 kira，mcmc/raman/make-mips 也无显著回退（合计 kira 5/20 vs 候选 5/19）→ **判为「该机制对本环境无影响」，evolve-1 的 −3.3pp 是 n=2 噪声**。四个题里三个由超时主导（gcode、make-mips 两臂全 0），压缩类机制在这类题上没有发挥空间；raman 的 −1 与 mcmc 的 +1 同属单次翻转量级，统计上不可区分。

> 附带结论（回应上面 H0 节的负载疑问）：confirm5 两臂同在低负载（load 5~15）窗口，`gcode-to-text` 仍 0/5 全超时、`raman-fitting` 1/5 → **这两个任务的超时主要是任务/模型固有，不是负载导致**；其余 6 个全败任务未在低负载复核。

**成本（Meta-Harness 相关，单独记账）**：优化器 $0.17 + 候选 smoke $0.02 + 首轮候选评估 $11.36 + confirm5 定向复验 $12.01 ≈ **$23.56**（terminus2 基线 $6.97 属 Phase 0 执行侧，另计）。
