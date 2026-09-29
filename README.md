# Knowledge-Guided Harness Evolution

研究目标：把经过核验的外部 harness 方法知识提供给优化 agent，结合任务需求、执行 trace 和自主探索，构建并迭代可验证的 agent harness。

完整研究动机、方法与分阶段规划见 [docs/research-plan.md](docs/research-plan.md)，前期论文与近邻工作结论见 [Idea 调研结果](docs/idea-research-findings.md)，四人分工见[三阶段并行执行计划](docs/team-execution-plan.md)。当前仓库已经开始保存可直接运行的方法代码，但尚无 benchmark 运行结果。

Terminal-Bench 2.0 数据、H0 参考快照和第一项方法知识已经完成静态准备；四份个人工作区均已保存独立 H0 副本，目前尚无 benchmark 运行结果。

## 目录

| 路径 | 用途 |
| --- | --- |
| `docs/` | 研究方案、协议和决策记录。 |
| `harness/h0/<name>/` | 可独立运行的初始执行 harness；当前包含 `terminus-kira`。 |
| `harness/candidates/` | 版本化候选 harness 的代码与配置；大体积运行产物不入库。 |
| `optimizer/initialization/` | 任务建模、方法选择、适配及 `H0 → H1` 的实现。 |
| `optimizer/evolution/` | trace 驱动的诊断、提案、验证与经验回写实现。 |
| `knowledge/sources/` | 外部论文与工程实践的来源索引和核验记录。 |
| `knowledge/` | 方法索引、方法说明与可运行代码；证据和原始材料独立保存。 |
| `benchmarks/` | benchmark 适配器、固定任务划分和评测协议。 |
| `experiments/` | baseline、消融和最终评估的可复现配置与脚本。 |
| `reproductions/<成员>/` | 每位成员独立的 Meta-Harness 代码、H0、配置、说明和本地运行路径。 |

## 当前执行顺序

1. 每位同学在个人工作区运行同一起点的独立 H0 副本，并记录环境、模型、trace、分数与成本。
2. 四位同学在 `reproductions/<成员>/meta-harness/` 中分别维护完整代码、H0、配置和运行产物；执行模型与优化模型均使用 `deepseek-v4-flash`，完成后交叉核对四份结果。
3. 打通知识引导的初始化与 trace 驱动优化闭环，再按测试协议评估。

评测运行器、任务数据和评分器不属于可优化的任务侧 harness。开发阶段不使用封存测试反馈挑选方法、调参或修改知识卡。

## 协作分支

`main` 保存共同协议和稳定骨架。成员分支分别为 `zhangXY/self-evolution-branch`、`zhouMF/self-evolution-branch`、`zhaoXY/self-evolution-branch`、`wangY/self-evolution-branch`、`yongK/self-evolution-branch`。共享协议和接口变更先在各自分支记录理由与验证，再合入 `main`。具体操作见 [GitHub 协作手册](CONTRIBUTING.md)。
