# Reproduction notes

Record environment preparation, commands, deviations from the paper, failures, and rerun instructions. Paths must remain inside this member workspace except for the shared read-only benchmark input.

## 本目录内容（周梦凡 / zhouMF）

| 文件 | 用途 |
| --- | --- |
| `reproduction-steps.md` | 权威步骤清单：按序复制即可重跑，每步标注产出、验收与状态。 |
| `reproduction-plan.md` | 规划与决策历史（为什么这么改、当时怎么判断、哪些结论后来被推翻）。 |
| `adaptations.md` | 与参考实现的代码/配置差异清单与离线验证记录。 |
| `run-log.md` | 逐次运行的实验条件、逐题 reward、token、费用、墙钟与异常。 |
| `reproduction-summary.md` | 验收对照、P6 结果、同口径复核、偏差与待办。 |
| `p1-env-report.txt` | P1 一键环境报告（uv / docker / 网络 / 免 provider 单测）。 |

路径约定：`configs/`、`notes/`、`results/`、`code-adaptation/` 都在本工作区
`reproductions/zhouMF/meta-harness/terminal-bench-2.0/` 下；共享的 Meta-Harness 上游副本在
`../code/reference_examples/terminal_bench_2/`（`jobs/`、`logs/` 在该目录下，已 gitignore）。
论文与官方代码来源见 `knowledge/source-packets/`；离线可运行 demo 见 `reproductions/zhouMF/method-reproduction/`。
