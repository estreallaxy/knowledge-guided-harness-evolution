# Knowledge-Guided Harness Evolution

研究目标：把经过核验的外部方法知识提供给优化 agent，结合任务需求、执行 trace 和自主探索，构建并迭代可验证的 agent harness。

## 目录

| 路径 | 用途 |
| --- | --- |
| [`knowledge/`](knowledge/) | 五人共享的方法知识来源、收集分工和整理规范。 |
| [`benchmarks/`](benchmarks/) | Terminal-Bench 2.0、GAIA2、SWE-Bench Pro 的共享只读代码与数据。 |
| [`reproductions/`](reproductions/) | 五位成员各自隔离的 H0、GEPA、Meta-Harness、AutoSaddler 复现代码与全部实验记录。 |
| [`docs/research-plan.md`](docs/research-plan.md) | 研究动机以及统一 baseline、benchmark。 |

五位成员主要修改 `knowledge/` 和 `reproductions/<本人>/`。共享 benchmark 不承载个人配置和结果；所有 baseline × benchmark 实验均在个人复现目录内闭合。协作流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。
