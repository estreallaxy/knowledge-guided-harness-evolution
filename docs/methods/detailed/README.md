# Harness 自进化 Method 详解

本目录保存五条独立 Method 的完整设计。五条路线共享四个阶段与同一个训练闭环，但采用不同的状态表示、候选生成机制、演化控制算法和长期复用方式。当前只确定方法设计，负责人均待分配。

## 共同的四个阶段

| 阶段 | 核心问题 | 共同输入 | 共同输出 |
| --- | --- | --- | --- |
| 1. 外部方法组织与检索 | 如何把论文和工程经验组织为可核验知识，并根据当前任务与 trace 找到适用方法？ | 固定来源包、当前 Harness、benchmark 训练 trace、历史经验 | 带来源锚点的方法表示、当前优化需求、候选方法及依赖闭包 |
| 2. 候选生成 | 如何结合 trace、检索知识和 `OptimizerLLM` 的自主探索产生可执行修改？ | 当前 Harness、故障解释、候选方法、允许编辑范围 | 通过接口、权限、数据隔离和静态检查的冻结候选 Harness |
| 3. 规划、测评与演化控制 | 如何选择最有决策价值的运行，比较父子 Harness，并控制多轮修改？ | 父子候选、训练/选择/anchor 任务、执行 trace、成本与风险 | 晋级、淘汰、继续取证、返回检索或返回候选生成的控制决定 |
| 4. 持续积累与跨任务复用 | 如何把正反证据、适用边界和失败经验写入长期状态？ | 本轮完整运行账本、候选谱系、模型/工具/环境版本 | 可审计的长期知识 revision、适用范围、反例、迁移条件与下一轮先验 |

阶段 1 的来源组织在 benchmark 演化 loop 外离线完成，在线检索属于 loop 内操作。其余三个阶段均在训练 loop 内运行。

## 最终闭环

1. 在 loop 外冻结论文、代码、配置、实验结果及其来源锚点，形成只读外部方法目录，同时封存 benchmark 测试集。
2. 从 benchmark 训练集划分本轮 trace、select 与 anchor 任务；执行当前父 Harness，产生带代码、工具、状态和结果事件的 trace。
3. 根据 trace 形成优化需求，检索外部方法；`OptimizerLLM` 结合检索知识与自主探索生成候选，`OptimizerHarness` 负责解析、核验和冻结。
4. 在训练任务上逐步运行最有决策价值的候选或 probe，用真实证据决定晋级、淘汰、继续取证，或返回前序阶段修订检索与候选。
5. 将本轮正反证据、适用边界、失败归因和调用记录原子写入长期状态。若候选晋级，则以新 Harness 进入下一轮；未晋级时保留父 Harness，但下一轮仍使用更新后的知识状态。
6. 当完整训练轮换中不再出现可改变决定的合法动作，并且回归、未知项和长期状态均满足停止条件后，冻结最终系统；只在此后运行 benchmark 测试集，测试结果不回流优化 loop。

## 五条 Method

| Method | 抽象设计思路 | 负责人 | 详解 |
| --- | --- | --- | --- |
| 证据约束的反例演化 | 把每次 Harness 修改视为可反驳假设：外部方法提供机制先验，trace 提供当前故障证据，真实反例持续收紧因果解释、接入条件和适用范围。 | 待分配 | [完整 Method](evidence-constrained-counterexample-evolution-detailed.md) |
| 程序结构库与渐增拓扑协同演化 | 把 Harness 表示为带类型、状态与副作用的程序图；检索可复用结构 motif，并让组件内容与调用拓扑在反例约束下共同生长。 | 待分配 | [完整 Method](program-structure-and-incremental-topology-coevolution-detailed.md) |
| 条件化案例与优化器组合 | 把外部经验组织为条件案例，把不同优化策略组织成可组合程序；根据当前失败区域选择互补策略，并对生成、接入、激活和效果分层分配信用。 | 待分配 | [完整 Method](conditional-cases-and-optimizer-portfolio-detailed.md) |
| 实验驱动的干预版本空间演化 | 把候选修改表示为带前提、预测和 typed holes 的干预假设；维护仍与证据一致的版本空间，通过判别实验逐步排除、特化或重组假设。 | 待分配 | [完整 Method](empirical-intervention-version-space-evolution-detailed.md) |
| 决策论驱动的信念演化 | 用显式 belief 表示故障原因、方法迁移、候选效果和评测可靠性；统一比较取证、计算、修改、回滚与停止动作，只执行最可能改变最终 Harness 选择的动作。 | 待分配 | [完整 Method](decision-theoretic-belief-evolution-detailed.md) |
