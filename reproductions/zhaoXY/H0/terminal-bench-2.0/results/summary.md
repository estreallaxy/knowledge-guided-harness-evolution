# Result summary — H0 × Terminal-Bench 2.0

由 `summarize.py` 从本地 job 目录生成（原始产物不入库）。

| Field | Value |
| --- | --- |
| Baseline | H0 = `terminus-kira`（`agents.baseline_kira:AgentHarness`，本单元 `code/terminus-kira/baseline_kira.py`，sha256 `e06b9273…`） |
| Benchmark | Terminal-Bench 2.0（仓库冻结快照，本地 Docker 后端） |
| Dataset split | train（30 题，`benchmarks/terminal-bench-2.0/split-v1.json`） |
| Model | `deepseek/deepseek-v4-flash`（API 实际标识 `deepseek-flash`，2026-10-13 核实），temperature 0.7 |
| Run id | `h0-terminal-bench-2.0-20261013-1`（2026-10-13T00:56:12.091372 → 2026-10-13T06:49:27.388988） |
| **Score** | **pass@2 = 0.6333**（19/30）；avg_score（计入判分题）= 0.6552 |
| Successful / failed / ungraded | 19 / 10 / 1 |
| Trials | 60 总数（完成 60、出错 19、重试 0）；trial-level micro pass rate = 0.55（33/60） |
| Tokens / cost / elapsed | 338761754 in（缓存 0）/ 5260141 out · $9.5112 · 21195 s（job 首启→最终结束的总跨度；若中途执行过 `harbor job resume`，该跨度含中断间隔，实际计算墙钟见 `../notes/stage1-summary.md`） |
| Config path | `configs/h0.yaml`（`command` 字段即实跑命令） |
| Trace path | 本地不入库：`runs/jobs/h0-terminal-bench-2.0-20261013-1/<task>__<id>/agent/trajectory.json` |

## 计算口径

- **pass@2**：每题 2 次 attempt，取最高分为该题得分；1.0 记 success。
- 分母固定为 30（题数）；未判分题（无 verifier 终判）计入分母、不计入 avg_score。
- 状态：success（最高分 1.0）/ failed（最高分 0.0）/ ungraded（无有效判分）。
- **trial-level micro pass rate**（trial 级通过率，与 main 上各线文档同一术语）= 33/60 = 0.55。
- 两个口径不可互换：任务级 pass@k 衡量「该题是否解出」，trial 级对每次尝试平均。
- tokens / cost 取 job `result.json` 的 stats；逐题明细见 `summary.json` 与本地 trial 目录。

## 逐题结果（run `h0-terminal-bench-2.0-20261013-1`）

| task | score | status | cost $ | wall s | exception |
| --- | --- | --- | --- | --- | --- |
| bn-fit-modify | 1.0 | success | 0.125 | 397 | — |
| caffe-cifar-10 | 0.0 | failed | 0.376 | 1509 | AgentTimeoutError；AgentTimeoutError |
| compile-compcert | 0.0 | failed | 0.812 | 2482 | AgentTimeoutError；AgentTimeoutError |
| custom-memory-heap-crash | 1.0 | success | 0.151 | 452 | — |
| dna-assembly | 0.0 | failed | 0.633 | 1884 | AgentTimeoutError；AgentTimeoutError |
| extract-moves-from-video | 0.0 | failed | 0.545 | 1908 | AgentTimeoutError；AgentTimeoutError |
| fix-code-vulnerability | 1.0 | success | 0.030 | 102 | — |
| fix-ocaml-gc | 1.0 | success | 0.547 | 3513 | — |
| gcode-to-text | 0.0 | failed | 0.339 | 941 | AgentTimeoutError；AgentTimeoutError |
| git-multibranch | 1.0 | success | 0.132 | 461 | — |
| headless-terminal | 1.0 | success | 0.212 | 936 | — |
| hf-model-inference | 1.0 | success | 0.078 | 536 | — |
| llm-inference-batching-scheduler | 1.0 | success | 0.278 | 809 | — |
| mailman | 1.0 | success | 0.572 | 1886 | AgentTimeoutError |
| make-mips-interpreter | 0.0 | failed | 0.777 | 1961 | AgentTimeoutError |
| mcmc-sampling-stan | 1.0 | success | 0.350 | 1593 | — |
| mteb-retrieve | 1.0 | success | 0.208 | 978 | — |
| polyglot-c-py | 1.0 | success | 0.090 | 351 | — |
| portfolio-optimization | 1.0 | success | 0.099 | 458 | — |
| pypi-server | 1.0 | success | 0.075 | 270 | — |
| pytorch-model-cli | 1.0 | success | 0.186 | 697 | — |
| qemu-alpine-ssh | 0.0 | failed | 0.299 | 926 | AgentTimeoutError |
| query-optimize | null | ungraded | 0.195 | 1487 | VerifierTimeoutError；VerifierTimeoutError |
| raman-fitting | 0.0 | failed | 0.328 | 938 | AgentTimeoutError；AgentTimeoutError |
| regex-log | 1.0 | success | 0.225 | 726 | — |
| sam-cell-seg | 0.0 | failed | 0.573 | 1847 | — |
| sanitize-git-repo | 1.0 | success | 0.117 | 345 | — |
| schemelike-metacircular-eval | 1.0 | success | 0.681 | 2344 | — |
| torch-pipeline-parallelism | 0.0 | failed | 0.281 | 1578 | VerifierTimeoutError；AgentTimeoutError |
| winning-avg-corewars | 1.0 | success | 0.195 | 907 | — |

## trial 级异常分布

| exception_type | trials |
| --- | --- |
| AgentTimeoutError | 16 |
| VerifierTimeoutError | 3 |
