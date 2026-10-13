# 方法知识收集与整理

`source-packets/` 保存五条 Method 共用的论文与工程来源。每个来源包固定论文版本、官方代码版本、精确来源位置、配置示例以及测试和报告结果；派生分析不得覆盖原始来源。

## 收集范围与分工

以下每个方向均收录 10 篇近两年正式顶会论文。每篇均有官方开源代码，并已经整理为完整 `SourcePacket`；跨方向来源只保存一份，通过方向索引复用。

| 收集方向 | 负责人 | 进度 | SourcePacket |
| --- | --- | --- | --- |
| 指令与 Skill | 周梦凡 | 10 / 10 | [ToolMaker](source-packets/toolmaker-2502.11705/)；[EASYTOOL](source-packets/easytool-2401.06201/)；[Tool-MVR](source-packets/tool-mvr-2506.04625/)；[SiriuS](source-packets/sirius-2502.04780/)；[MAGIC](source-packets/magic-2406.12692/)；[G-Memory](source-packets/g-memory-2506.07398/)；[AgentDropout](source-packets/agentdropout-2503.18891/)；[500xCompressor](source-packets/500xcompressor-2408.03094/)；[InferenceDynamics](source-packets/inference-dynamics-2505.16303/)；[GuardAgent](source-packets/guardagent-2406.09187/) |
| 工具与环境交互 | 赵星源 | 10 / 10 | [ToolMaker](source-packets/toolmaker-2502.11705/)；[EASYTOOL](source-packets/easytool-2401.06201/)；[Tool-MVR](source-packets/tool-mvr-2506.04625/)；[Fail-TALMs](source-packets/fail-talms-2503.14227/)；[GUI-Robust](source-packets/gui-robust-2506.14477/)；[DRIFT](source-packets/drift-2506.12104/)；[WASP](source-packets/wasp-2504.18575/)；[AgentDojo](source-packets/agentdojo-2406.13352/)；[GuardAgent](source-packets/guardagent-2406.09187/)；[AgentAuditor](source-packets/agentauditor-2506.00641/) |
| 上下文管理与压缩 | 周梦凡 | 10 / 10 | [500xCompressor](source-packets/500xcompressor-2408.03094/)；[DAC](source-packets/dac-2507.11942/)；[G-Memory](source-packets/g-memory-2506.07398/)；[Hello Again!](source-packets/hello-again-2406.05925/)；[EASYTOOL](source-packets/easytool-2401.06201/)；[GUI-Robust](source-packets/gui-robust-2506.14477/)；[AgentDropout](source-packets/agentdropout-2503.18891/)；[SiriuS](source-packets/sirius-2502.04780/)；[RAGRouter](source-packets/ragrouter-2505.23052/)；[SGLang](source-packets/sglang-2312.07104/) |
| 长期记忆与经验复用 | 李永康 | 10 / 10 | [G-Memory](source-packets/g-memory-2506.07398/)；[Hello Again!](source-packets/hello-again-2406.05925/)；[SiriuS](source-packets/sirius-2502.04780/)；[MAGIC](source-packets/magic-2406.12692/)；[GuardAgent](source-packets/guardagent-2406.09187/)；[AGDebugger](source-packets/agdebugger-2503.02068/)；[Collab-Overcooked](source-packets/collab-overcooked-2502.20073/)；[AgentSense](source-packets/agentsense-2410.19346/)；[TAIRA](source-packets/taira-2506.23485/)；[AgentAuditor](source-packets/agentauditor-2506.00641/) |
| 容错与故障恢复 | 赵星源 | 10 / 10 | [GUI-Robust](source-packets/gui-robust-2506.14477/)；[Fail-TALMs](source-packets/fail-talms-2503.14227/)；[DRIFT](source-packets/drift-2506.12104/)；[MAGIC](source-packets/magic-2406.12692/)；[SiriuS](source-packets/sirius-2502.04780/)；[WASP](source-packets/wasp-2504.18575/)；[OS-Harm](source-packets/os-harm-2506.14866/)；[AgentDojo](source-packets/agentdojo-2406.13352/)；[AGDebugger](source-packets/agdebugger-2503.02068/)；[GuardAgent](source-packets/guardagent-2406.09187/) |
| 执行循环与调度 | 赵星源 | 10 / 10 | [AgentDropout](source-packets/agentdropout-2503.18891/)；[SiriuS](source-packets/sirius-2502.04780/)；[G-Memory](source-packets/g-memory-2506.07398/)；[ToolMaker](source-packets/toolmaker-2502.11705/)；[AgentDojo](source-packets/agentdojo-2406.13352/)；[SGLang](source-packets/sglang-2312.07104/)；[Tool-MVR](source-packets/tool-mvr-2506.04625/)；[MAGIC](source-packets/magic-2406.12692/)；[MultiAgentBench](source-packets/multiagentbench-2503.01935/)；[MESS+](source-packets/mess-plus-2505.19947/) |
| 规划与任务进度管理 | 李嘉旺 | 10 / 10 | [TAIRA](source-packets/taira-2506.23485/)；[LLM Planning Formalizers](source-packets/llm-planning-formalizers-2412.09879/)；[Agent Planning Barriers](source-packets/agent-planning-barriers-2410.12409/)；[MAGIC](source-packets/magic-2406.12692/)；[SiriuS](source-packets/sirius-2502.04780/)；[G-Memory](source-packets/g-memory-2506.07398/)；[AgentDropout](source-packets/agentdropout-2503.18891/)；[MultiAgentBench](source-packets/multiagentbench-2503.01935/)；[CoMLRL](source-packets/comlrl-2508.04652/)；[GuardAgent](source-packets/guardagent-2406.09187/) |
| 模型选择与资源分配 | 周梦凡 | 10 / 10 | [IRT-Router](source-packets/irt-router-2506.01048/)；[AgentDropout](source-packets/agentdropout-2503.18891/)；[MasRouter](source-packets/masrouter-2502.11133/)；[MESS+](source-packets/mess-plus-2505.19947/)；[Lookahead Routing](source-packets/lookahead-routing-2510.19506/)；[RAGRouter](source-packets/ragrouter-2505.23052/)；[Smoothie](source-packets/smoothie-2412.04692/)；[SGLang](source-packets/sglang-2312.07104/)；[InferenceDynamics](source-packets/inference-dynamics-2505.16303/)；[ICL-Router](source-packets/icl-router-2510.09719/) |
| 会话与环境状态管理 | 李永康 | 10 / 10 | [G-Memory](source-packets/g-memory-2506.07398/)；[Hello Again!](source-packets/hello-again-2406.05925/)；[GUI-Robust](source-packets/gui-robust-2506.14477/)；[AgentDojo](source-packets/agentdojo-2406.13352/)；[AGDebugger](source-packets/agdebugger-2503.02068/)；[SiriuS](source-packets/sirius-2502.04780/)；[MultiAgentBench](source-packets/multiagentbench-2503.01935/)；[CoMLRL](source-packets/comlrl-2508.04652/)；[WASP](source-packets/wasp-2504.18575/)；[DRIFT](source-packets/drift-2506.12104/) |
| 子 Agent 与多 Agent 协作 | 王懿 | 10 / 10 | [AgentDropout](source-packets/agentdropout-2503.18891/)；[MultiAgentBench](source-packets/multiagentbench-2503.01935/)；[Collab-Overcooked](source-packets/collab-overcooked-2502.20073/)；[SiriuS](source-packets/sirius-2502.04780/)；[G-Memory](source-packets/g-memory-2506.07398/)；[CoMLRL](source-packets/comlrl-2508.04652/)；[MasRouter](source-packets/masrouter-2502.11133/)；[AGDebugger](source-packets/agdebugger-2503.02068/)；[AgentSense](source-packets/agentsense-2410.19346/)；[AgentAuditor](source-packets/agentauditor-2506.00641/) |
| 权限、审批与运行隔离 | 李嘉旺 | 10 / 10 | [DRIFT](source-packets/drift-2506.12104/)；[WASP](source-packets/wasp-2504.18575/)；[OS-Harm](source-packets/os-harm-2506.14866/)；[AgentDAM](source-packets/agentdam-2503.09780/)；[AgentDojo](source-packets/agentdojo-2406.13352/)；[GuardAgent](source-packets/guardagent-2406.09187/)；[AgentAuditor](source-packets/agentauditor-2506.00641/)；[GUI-Robust](source-packets/gui-robust-2506.14477/)；[Fail-TALMs](source-packets/fail-talms-2503.14227/)；[Agent-RewardBench](source-packets/agent-rewardbench-2506.21252/) |
| 扩展机制与生命周期钩子 | 李永康 | 10 / 10 | [SGLang](source-packets/sglang-2312.07104/)；[ToolMaker](source-packets/toolmaker-2502.11705/)；[AgentDropout](source-packets/agentdropout-2503.18891/)；[MultiAgentBench](source-packets/multiagentbench-2503.01935/)；[AgentDojo](source-packets/agentdojo-2406.13352/)；[G-Memory](source-packets/g-memory-2506.07398/)；[SiriuS](source-packets/sirius-2502.04780/)；[EASYTOOL](source-packets/easytool-2401.06201/)；[MasRouter](source-packets/masrouter-2502.11133/)；[AGDebugger](source-packets/agdebugger-2503.02068/) |
| 运行观测、Trace 与集成接口 | 王懿 | 10 / 10 | [G-Memory](source-packets/g-memory-2506.07398/)；[AGDebugger](source-packets/agdebugger-2503.02068/)；[SiriuS](source-packets/sirius-2502.04780/)；[MultiAgentBench](source-packets/multiagentbench-2503.01935/)；[GUI-Robust](source-packets/gui-robust-2506.14477/)；[Fail-TALMs](source-packets/fail-talms-2503.14227/)；[Tool-MVR](source-packets/tool-mvr-2506.04625/)；[AgentAuditor](source-packets/agentauditor-2506.00641/)；[WASP](source-packets/wasp-2504.18575/)；[AgentDojo](source-packets/agentdojo-2406.13352/) |
| 验证、评估与反馈 | 李嘉旺 | 10 / 10 | [Agent-RewardBench](source-packets/agent-rewardbench-2506.21252/)；[AgentSense](source-packets/agentsense-2410.19346/)；[Collab-Overcooked](source-packets/collab-overcooked-2502.20073/)；[MultiAgentBench](source-packets/multiagentbench-2503.01935/)；[OS-Harm](source-packets/os-harm-2506.14866/)；[WASP](source-packets/wasp-2504.18575/)；[AgentDAM](source-packets/agentdam-2503.09780/)；[Fail-TALMs](source-packets/fail-talms-2503.14227/)；[AgentAuditor](source-packets/agentauditor-2506.00641/)；[AgentDojo](source-packets/agentdojo-2406.13352/) |

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
