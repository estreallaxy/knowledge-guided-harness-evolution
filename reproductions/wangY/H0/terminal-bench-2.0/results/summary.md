# Result summary

| Field | Value |
| --- | --- |
| Baseline | H0 / kira-baseline（`agents.baseline_kira:AgentHarness`，纯上游未改动，sha256 `e06b9273…eb889`） |
| Benchmark | Terminal-Bench 2.0（`terminal-bench@2.0`，commit `69671fbaac6d67a7ef0dfec016cc38a64ef7a77c`，harbor 0.18.0 runner） |
| Code revision | H0 快照见 `../../UPSTREAM.md`（harbor `dc933be7…`，meta-harness `8123ccab…`）；运行入口为 `reproductions/wangY/meta-harness/code/reference_examples/terminal_bench_2/` |
| H0 revision | `baseline_kira.py` sha256 `e06b9273e2b900006a2072457dff2630ad04e589c48057d050219bdc791eb889` |
| Dataset split | `train`（30 题，`benchmarks/terminal-bench-2.0/split-v1.json`，seed `kghe-tb2-v1-2026-09-27`；本机上生成的划分目录 `/data1/users/wangY/benchmarks/tb2-split-v1/train`） |
| Model and provider | `deepseek/deepseek-flash`（团队约定 deepseek-v4-flash；DeepSeek OpenAI 兼容端点 `https://api.deepseek.com/v1`），temperature 0.7 |
| Random seed | 采样无固定 seed（API 侧默认）；任务集合由 split 清单 seed `kghe-tb2-v1-2026-09-27` 固定 |
| Score | **pass@2 = 0.70**（21/30）；avg_score = 0.7241（21/29，未判分题不计入）；config_hash `b10d4d81c1fcccc80f26b488fcfe82e3b56c200f62d479053a14f1b739a650e5` |
| Successful / failed / ungraded | 21 / 8 / 1（query-optimize：两次 attempt 判分器均 900s 超时，score=null，**计入分母 30**） |
| Tokens / calls / cost / elapsed time | 323.3M in / 5.57M out（60 trials 合计，输入 ~99% 缓存命中）；$9.7676（job `result.json` 口径）；总墙钟 31084.5 s（分段累计，含两次余额中断与续跑） |
| Config path | `../configs/h0.yaml` |
| Trace path | 本地不入库：`../../runs/jobs/h0-terminal-bench-2.0-20261009-1/`（60 个 trial 原始目录）、`../../traces/h0-terminal-bench-2.0-20261009-1/`（计分 attempt 轨迹）；逐题轨迹指针见同目录 `per-task.jsonl`（本地保留）与下表 |
| Notes | 运行因 DeepSeek 余额耗尽中断一次，用 `harbor job resume` 分 3 段补跑、全部落回同一 job 目录；实际并发 8 < 配置 50（只影响墙钟）。完整过程与口径见 `../notes/stage1-summary.md`。 |

## 计算口径

- **pass@2**：一道题两次 attempt（`--trials 2`），取两次中的最高分为该题 score；score=1.0 记 success。分母固定为 30（题数），**未判分题计入分母、不计入 avg_score 分母**。
- 状态：success（任一次 1.0）/ failed（出现有效 0.0 终判）/ timeout（两次均为超时类异常、无有效判分）。
- AgentTimeout 甄别：两次 attempt 均到达题目 `task.toml` 声明时限（900/1200/1800 s）的，按任务真实超时记 0.0 终判、不再重跑；发生在 job 被余额中断时刻的按环境性中止重排。

## 逐题结果（run `h0-terminal-bench-2.0-20261009-1`）

| task_id | score | status | cost $ | wall s | error |
| --- | --- | --- | --- | --- | --- |
| bn-fit-modify | 1.0 | success | 0.148 | 437 | — |
| caffe-cifar-10 | 0.0 | failed | 0.171 | 2272 | AgentTimeout ×2（1200s） |
| compile-compcert | 1.0 | success | 0.935 | 2414 | — |
| custom-memory-heap-crash | 1.0 | success | 0.122 | 395 | — |
| dna-assembly | 1.0 | success | 0.832 | 1826 | — |
| extract-moves-from-video | 0.0 | failed | 0.590 | 1866 | AgentTimeout ×2（1800s） |
| fix-code-vulnerability | 1.0 | success | 0.063 | 222 | — |
| fix-ocaml-gc | 1.0 | success | 0.389 | 1573 | — |
| gcode-to-text | 0.0 | failed | 0.458 | 940 | AgentTimeout ×2（900s） |
| git-multibranch | 1.0 | success | 0.267 | 656 | — |
| headless-terminal | 1.0 | success | 0.109 | 320 | — |
| hf-model-inference | 1.0 | success | 0.078 | 278 | — |
| llm-inference-batching-scheduler | 1.0 | success | 0.228 | 458 | — |
| mailman | 1.0 | success | 0.468 | 1334 | — |
| make-mips-interpreter | 0.0 | failed | 0.826 | 1863 | attempt2 AgentTimeout（1800s），attempt1 判 0 |
| mcmc-sampling-stan | 1.0 | success | 0.520 | 1727 | — |
| mteb-retrieve | 1.0 | success | 0.169 | 552 | — |
| polyglot-c-py | 1.0 | success | 0.115 | 338 | — |
| portfolio-optimization | 1.0 | success | 0.093 | 436 | — |
| pypi-server | 1.0 | success | 0.071 | 233 | — |
| pytorch-model-cli | 1.0 | success | 0.203 | 586 | — |
| qemu-alpine-ssh | 0.0 | failed | 0.277 | 871 | —（两次均正常判 0） |
| query-optimize | null | timeout | 0.164 | 1302 | VerifierTimeout ×2（判分器 900s；空闲重跑仍超时，记该题 cpus=1 容器内真实判分上限） |
| raman-fitting | 0.0 | failed | 0.422 | 939 | AgentTimeout ×2（900s） |
| regex-log | 1.0 | success | 0.266 | 616 | — |
| sam-cell-seg | 0.0 | failed | 0.499 | 1505 | —（两次均正常判 0） |
| sanitize-git-repo | 1.0 | success | 0.110 | 300 | — |
| schemelike-metacircular-eval | 1.0 | success | 0.525 | 1837 | — |
| torch-pipeline-parallelism | 0.0 | failed | 0.338 | 1852 | AgentTimeout ×2（900s） |
| winning-avg-corewars | 1.0 | success | 0.311 | 1134 | — |

资源字段（steps / tool_calls / tokens_in / tokens_out / 完整 error 文本 / trace 指针）逐题见同目录
`per-task.jsonl`（本地保留，不入库）与 `../runs/` 下的 job 原始目录；入库机读摘要为同目录 `summary.json`。
