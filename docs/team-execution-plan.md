# 团队执行计划

## 总体结构

阶段一完成当前已分配任务。进入阶段二后，五位成员分别进入一条独立线路；线路之间不共享复现产物、不共同实现 Method，也不依赖其他线路的中间结果。

每条线路内部包含两条工作链：

```text
阶段一：Meta-Harness × Terminal-Bench 2.0 + 每个负责方向 2 篇论文
   └─ 五条隔离线路并行启动
       ├─ Baseline 链：H0 → GEPA → Meta-Harness → AutoSaddler
       │               每个 baseline 分别复现 3 个 benchmark
       └─ Method 链：继续收集论文 → 分配 Method → 建独立仓库 → 实现与验证
```

同一线路内，Baseline 链与 Method 链并行；Method 链内部按照“论文收集 → Method 分配与建库 → 实现”的顺序执行。

## 阶段一：完成已分配任务

| 清单 | 执行要求 | 完成条件 |
| --- | --- | --- |
| 复现 `Meta-Harness × Terminal-Bench 2.0` | 五位成员分别在 `reproductions/<成员>/meta-harness/terminal-bench-2.0/` 保存源码、环境、配置、trace、分数、成本、失败记录和复现说明。 | 五个独立目录都能按各自说明启动，成功与失败运行均有完整记录。 |
| 收集负责方向的论文 | 按 [knowledge/README.md](../knowledge/README.md) 的既有分工，每个方向整理 2 个合格 `SourcePacket`，放入 `knowledge/source-packets/<source-id>/`，并更新知识索引。 | 每个方向达到 `2 / 2`；论文、官方代码、来源锚点、配置、测试和报告结果齐全，缺失项明确标为未知。 |

## 阶段二：五条隔离线路独立扩展

从本阶段开始，五条线路完全隔离并行。每位成员只在自己的 `reproductions/<成员>/` 中复现 baseline，只维护本线路负责的论文材料；任何其他线路的结果只能用于阅读，不能代替本线路复现或成为本线路实验结果。

### Baseline 链：分别复现 4 个 baseline × 3 个 benchmark

四个 baseline 必须作为四个独立复现项目分别完成，不能用其中一个 baseline 的环境、适配代码或结果代替另一个。

| 独立 baseline | 需要分别覆盖的 benchmark | 本线路存放位置 |
| --- | --- | --- |
| Benchmark H0 | Terminal-Bench 2.0、GAIA2、SWE-Bench Pro | `reproductions/<成员>/H0/<benchmark>/` |
| GEPA | Terminal-Bench 2.0、GAIA2、SWE-Bench Pro | `reproductions/<成员>/GEPA/<benchmark>/` |
| Meta-Harness | Terminal-Bench 2.0、GAIA2、SWE-Bench Pro | `reproductions/<成员>/meta-harness/<benchmark>/` |
| AutoSaddler | Terminal-Bench 2.0、GAIA2、SWE-Bench Pro | `reproductions/<成员>/AutoSaddler/<benchmark>/` |

每个 baseline × benchmark 组合独立保存源码 revision、依赖、模型、H0、数据划分、配置、seed、评测器、trace、结果、成本和失败记录。每条线路独立完成全部 12 个组合，不使用其他成员的运行结果补齐矩阵。

### Method 链：继续扩充并核验论文材料

| 清单 | 执行要求 | 完成条件 |
| --- | --- | --- |
| 完成本线路基础覆盖 | 补齐本成员在 `knowledge/README.md` 中负责的全部方向，每个方向至少 2 个合格来源包。 | 本线路负责方向全部达到基础覆盖，重复论文不重复计数。 |
| 补充关键机制 | 围绕组织与检索、候选生成、演化控制、持续积累四个阶段继续收集可迁移方法。 | 每个关键机制至少有可追溯论文或工程来源；没有成熟来源时登记知识缺口。 |
| 执行质量复核 | 核对论文版本、官方代码、原文锚点、实现接口、实验条件、收益、成本和失败边界。 | SourcePacket 通过结构检查和人工复核；未经核验内容不进入后续实现。 |

## 阶段三：分配 Method 并建立五个独立仓库

本阶段在各线路完成自身论文材料后分别启动。五份 Method 当前均待分配；确定分工后，每位成员只获得一个 Method 和一个独立 GitHub 仓库。

| Method | 负责人 | 独立 GitHub 仓库 | 建库前置条件 |
| --- | --- | --- | --- |
| 证据约束的反例演化 | 待分配 | 待创建 | Method 详解和本线路相关来源已冻结。 |
| 程序结构库与渐增拓扑协同演化 | 待分配 | 待创建 | Method 详解和本线路相关来源已冻结。 |
| 条件化案例与优化器组合 | 待分配 | 待创建 | Method 详解和本线路相关来源已冻结。 |
| 实验驱动的干预版本空间演化 | 待分配 | 待创建 | Method 详解和本线路相关来源已冻结。 |
| 决策论驱动的信念演化 | 待分配 | 待创建 | Method 详解和本线路相关来源已冻结。 |

每个仓库只放对应 Method 的详解、知识处理代码、候选 Harness 接口、trace/账本 schema、实验配置、测试和复现说明。不同 Method 的代码、运行状态和实验结果不放入同一仓库。

## 阶段四：各线路独立实现 Method

| 清单 | 执行要求 | 完成条件 |
| --- | --- | --- |
| 建立本 Method 的关系与索引 | 按该 Method 的状态表示，标注论文方法之间的依赖、替代、组合、冲突、适用条件及代码入口，并实现相应检索索引。 | 本 Method 能从当前任务与 trace 状态定位到可接入材料；索引不依赖其他线路的实现。 |
| 跑通单轮链路 | 外部方法检索 → trace 诊断 → 候选生成 → 核验 → 一次测评 → 状态写回。 | 每一步有真实输入、输出、调用记录和失败语义。 |
| 跑通多轮演化 | 支持 `H0 → H1 → H2 → ...`，包括返回检索、返回候选生成、回滚和停止。 | 训练 loop 可恢复、可重放，测试集始终隔离。 |
| 完成消融 | 分别移除外部知识、trace、自由探索和长期复用。 | 能区分各模块贡献，并记录性能与成本变化。 |
| 接入本线路 baseline | 使用本线路阶段二独立复现的 H0、GEPA、Meta-Harness 和 AutoSaddler 结果。 | Method 与 baseline 在本线路内部满足可比条件。 |

## 阶段五：各线路独立验证

| 清单 | 执行要求 | 完成条件 |
| --- | --- | --- |
| 主结果对比 | 本 Method 与本线路复现的 H0、GEPA、Meta-Harness、AutoSaddler 分别在三个 benchmark 上比较。 | 报告本线路一致条件下的效果、成本、方差和失败类型。 |
| 泛化与能力保留 | 检查未见任务、跨 benchmark 迁移、anchor 能力和严重失败。 | 新能力提升不以不可接受的旧能力退化为代价。 |
| 线路内复核 | 复核本线路的代码版本、数据角色、配置、日志、结果和结论。 | 所有主张可回到本线路仓库 revision、SourcePacket 或真实运行证据。 |

五条线路分别形成完整结果，不在本阶段合并代码、共享中间状态或用其他线路实验补齐自身结果。

## 五条独立线路

| 线路 | 成员 | 已分配知识方向 | 独立复现目录 | Method |
| --- | --- | --- | --- | --- |
| 线路 1 | 周梦凡 | 指令与 Skill；上下文管理与压缩；模型选择与资源分配 | `reproductions/zhouMF/` | 待分配 |
| 线路 2 | 赵星源 | 工具与环境交互；容错与故障恢复；执行循环与调度 | `reproductions/zhaoXY/` | 待分配 |
| 线路 3 | 王懿 | 子 Agent 与多 Agent 协作；运行观测、Trace 与集成接口 | `reproductions/wangY/` | 待分配 |
| 线路 4 | 李永康 | 长期记忆与经验复用；会话与环境状态管理；扩展机制与生命周期钩子 | `reproductions/liYK/` | 待分配 |
| 线路 5 | 李嘉旺 | 规划与任务进度管理；权限、审批与运行隔离；验证、评估与反馈 | `reproductions/liJW/` | 待分配 |
