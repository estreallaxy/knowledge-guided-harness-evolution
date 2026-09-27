# Knowledge-Guided Harness Evolution

研究目标：把经过核验的外部 harness 方法知识提供给优化 agent，结合任务需求、执行 trace 和自主探索，构建并迭代可验证的 agent harness。

完整研究动机、方法与分阶段规划见 [docs/research-plan.md](docs/research-plan.md)。当前仓库只搭建共同开发骨架，不包含已实现的方法或已复现的实验结果。

## 目录

| 路径 | 用途 |
| --- | --- |
| `docs/` | 研究方案、协议和决策记录。 |
| `harness/h0/` | 各方法共用的初始执行 harness；任务侧代码和配置作为优化对象。 |
| `harness/candidates/` | 版本化候选 harness 的代码与配置；大体积运行产物不入库。 |
| `optimizer/initialization/` | 任务建模、方法选择、适配及 `H0 → H1` 的实现。 |
| `optimizer/evolution/` | trace 驱动的诊断、提案、验证与经验回写实现。 |
| `knowledge/sources/` | 外部论文与工程实践的来源索引和核验记录。 |
| `knowledge/method-cards/` | 经复核的方法卡；从 `TEMPLATE.md` 开始。 |
| `benchmarks/` | benchmark 适配器、固定任务划分和评测协议。 |
| `experiments/` | baseline、消融和最终评估的可复现配置与脚本。 |

## 当前执行顺序

1. 核对 Meta-Harness 与 Terminal-Bench 2.0 的可运行性，固定训练、开发、测试划分及预算。
2. 确定可编辑的共同 `H0`，在同一开发任务上重跑 `H0` 和方法 baseline。
3. 从“指令与 Skill”方向选择一篇论文，制作并人工复核首张方法卡。
4. 打通知识引导的初始化与 trace 驱动优化闭环，再按封存测试协议评估。

评测运行器、任务数据和评分器不属于可优化的任务侧 harness。开发阶段不使用封存测试反馈挑选方法、调参或修改知识卡。

## 协作分支

`main` 保存共同协议和稳定骨架。四位成员分别从 `main` 建立 `zhangXY/self-evolution-branch`、`zhouMF/self-evolution-branch`、`zhaoXY/self-evolution-branch`、`wangY/self-evolution-branch`。共享协议和接口变更先在各自分支记录理由与验证，再合入 `main`。
