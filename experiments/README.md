| 实验 | 执行 Harness | 优化方法 | Benchmark | 状态 | 结果 |
| --- | --- | --- | --- | --- | --- |
| H0 + Terminal-Bench 2.0 | 每人 `code/reference_examples/terminal_bench_2/agents/baseline_kira.py` | 无 | [Terminal-Bench 2.0](../benchmarks/terminal-bench-2.0/README.md) | 待运行 | 分别保存在 `reproductions/<成员>/meta-harness/runs/` |
| Meta-Harness + Terminal-Bench 2.0 | 每人工作区内的 H0 | 每人 `code/reference_examples/terminal_bench_2/meta_harness.py` | [Terminal-Bench 2.0](../benchmarks/terminal-bench-2.0/README.md) | 待复现 | 分别保存在 `reproductions/<成员>/meta-harness/runs/` |

结果字段约定与缺失记录检查见 [`results/README.md`](results/README.md)。原始运行产物保存在各成员工作区的 `reproductions/<成员>/meta-harness/runs/`；字段文档入库，原始 trace 与 jsonl 默认不入库。
