# 方法知识收集与整理

`source-packets/` 保存五条 Method 共用的论文与工程来源。每个来源包固定论文版本、官方代码版本、精确来源位置、配置示例以及测试和报告结果；派生分析不得覆盖原始来源。

## 收集范围与分工

| 收集方向 | 负责人 | 进度 | 论文、GitHub 与来源包 |
| --- | --- | --- | --- |
| 指令与 Skill | 周梦凡 | 1 / 2 | [Skill Usage](source-packets/skill-usage-2604.04323/) · [论文](https://arxiv.org/abs/2604.04323v1) · [GitHub](https://github.com/UCSB-NLP-Chang/Skill-Usage) |
| 工具与环境交互 | 赵星源 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 上下文管理与压缩 | 周梦凡 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 长期记忆与经验复用 | 李永康 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 容错与故障恢复 | 赵星源 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 执行循环与调度 | 赵星源 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 规划与任务进度管理 | 李嘉旺 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 模型选择与资源分配 | 周梦凡 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 会话与环境状态管理 | 李永康 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 子 Agent 与多 Agent 协作 | 王懿 | 2 / 2 | [AutoGen](source-packets/autogen-2308.08155/) · [论文](https://arxiv.org/abs/2308.08155v2) · [GitHub](https://github.com/microsoft/autogen)；[MetaGPT](source-packets/metagpt-2308.00352/) · [论文](https://arxiv.org/abs/2308.00352v7) · [GitHub](https://github.com/geekan/MetaGPT) |
| 权限、审批与运行隔离 | 李嘉旺 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 扩展机制与生命周期钩子 | 李永康 | 0 / 2 | 待按 `SourcePacket` 收集。 |
| 运行观测、Trace 与集成接口 | 王懿 | 2 / 2 | [SWE-agent](source-packets/swe-agent-2405.15793/) · [论文](https://arxiv.org/abs/2405.15793v3) · [GitHub](https://github.com/princeton-nlp/SWE-agent)；[OpenHands](source-packets/openhands-2407.16741/) · [论文](https://arxiv.org/abs/2407.16741v3) · [GitHub](https://github.com/All-Hands-AI/OpenHands) |
| 验证、评估与反馈 | 李嘉旺 | 0 / 2 | 待按 `SourcePacket` 收集。 |

## 筛选标准

| 核心评价指标 | 如何使用该指标进行评价 |
| --- | --- |
| 问题相关性 | 是否解决目标任务或 harness 的具体瓶颈；与已发现失败类型和优化需求直接相关的优先。 |
| 机制清晰度与可迁移性 | 是否说明改什么、如何改、何时适用，以及迁移所需模型、训练和环境条件。 |
| 证据可信度 | 是否有可追溯原始材料、公平对照、消融或重复实验；区分“已经实现”“整体系统有效”和“该机制有效”。 |
| 收益与代价 | 同时记录成功率、可靠性、token、时延、复杂度及对原有能力的影响。 |
| 可复现性与落地成本 | 核心代码、配置和方法描述是否足以接入并验证；价值相近时优先可复现方案。 |
| 知识增量与互补性 | 是否补充新机制、新适用条件或不同成本收益取舍；降低重复材料优先级。 |

## 来源包内容

| 要做什么 | 每个来源包需要回答或保留的内容 |
| --- | --- |
| 提取机制 | 目标瓶颈、作用模块、输入、触发条件、必要步骤、状态变化和预期输出。 |
| 标注使用边界 | 所需任务、模型、工具、环境和预算；已知失效条件与尚未验证条件。 |
| 绑定实现与效果 | 论文、代码和配置版本；原文位置、关键接口、示例、对照、收益、成本与副作用。 |
| 建立方法关系 | 依赖、替代、组合、冲突或变体；区分已有证据与待测假设。 |
| 核验并入库 | 自动检查链接、版本和数值，运行可行的最小示例；人工复核机制、遗漏条件和错误归因，缺失信息写“未知”。 |

## 持续维护

| 知识维护 | 要做什么 |
| --- | --- |
| 关联外部与内部证据 | 把方法连接到采用、改造、组合或拒绝它的 harness 修改与实验记录。 |
| 更新适用范围 | 区分机制已核实、当前任务局部有效、未见同类任务有效和跨环境有效。 |
| 处理重复与冲突 | 按机制和条件关联近似方法；并列记录冲突结论及任务、模型、harness、预算、评测器和版本。 |
| 处理过时与误导 | 上游接口、模型或 benchmark 变化，或迁移实验出现退化时，标记待复查并暂停主动推荐。 |

当前来源包索引见 [source-packets/README.md](source-packets/README.md)。
