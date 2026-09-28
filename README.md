# Knowledge-Guided Harness Evolution

研究目标：把经过核验的外部 harness 方法知识提供给优化 agent，结合任务需求、执行 trace 和自主探索，构建并迭代可验证的 agent harness。

完整研究动机、方法与分阶段规划见 [docs/research-plan.md](docs/research-plan.md)。当前仓库已经开始保存可直接运行的方法代码，但尚无 benchmark 运行结果。

Terminal-Bench 2.0 数据、共同 H0 和第一项方法知识已经完成静态准备；目前尚无 benchmark 运行结果。

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

## 当前执行顺序

1. 在 Terminal-Bench 2.0 的训练任务上运行共同 H0，并记录环境、模型、trace、分数与成本。
2. 在相同设置下复现 Meta-Harness，区分论文原设置与共同协议下的适配结果。
3. 打通知识引导的初始化与 trace 驱动优化闭环，再按测试协议评估。

评测运行器、任务数据和评分器不属于可优化的任务侧 harness。开发阶段不使用封存测试反馈挑选方法、调参或修改知识卡。

## 协作分支

`main` 保存共同协议和稳定骨架。四个成员分支分别为 `zhangXY/self-evolution-branch`、`zhouMF/self-evolution-branch`、`zhaoXY/self-evolution-branch`、`wangY/self-evolution-branch`。共享协议和接口变更先在各自分支记录理由与验证，再合入 `main`。具体操作见 [GitHub 协作手册](CONTRIBUTING.md)。
