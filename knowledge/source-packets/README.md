# Source Packets

每篇论文使用一个独立目录，目录名采用 `<短标题>-<arXiv编号或其他稳定标识>`。五位成员可以并行新增目录，不在这里保存某条 Method 的派生表示。

每个来源包必须包含：

```text
<paper-id>/
├── source-packet.json
├── paper/
│   ├── paper-vN.pdf
│   └── paper-vN.txt
├── official-code/
├── exact-source-anchors.md
├── configs-and-examples.md
└── tests-and-reported-results.md
```

| `SourcePacket` 字段 | 必须记录的内容 |
| --- | --- |
| `paper_version` | 论文题目、作者、版本、发布日期、来源 URL、本地 PDF 与文本路径。 |
| `official_code_version` | 官方仓库、固定上游 revision、获取日期、本地代码范围及许可证状态。 |
| `exact_source_anchors` | 每条机制、条件和限制在论文页码、章节、图表及代码文件中的精确位置。 |
| `configs_and_examples` | 论文或官方仓库实际使用的配置、命令、数据入口和运行前提。 |
| `tests_and_reported_results` | 官方测试入口、论文报告结果、消融、失败条件及本地复核状态。 |

收集时遵守以下规则：

1. 原始来源与后续 Method 派生物分开；来源包不提前写入某条路线的对象结构。
2. 论文与官方代码版本不能使用“最新版”代替；更新时新增版本记录，不覆盖旧材料。
3. 论文报告、代码实际行为和本地运行结果分别记录，缺失信息写明未知。
4. 不提交密钥、运行缓存、大型外部数据集或由 benchmark 泄露的测试答案。
5. 同一论文目录由提交者在合并前负责消解冲突；不同论文目录可以并行新增。
6. `official-code/` 围绕论文方法选择材料；允许保留机制所需的 evaluator、scorer、测试、配置和示例，不要求仅因文件属于评测流程就删除。不得纳入密钥、登录状态或直接暴露 benchmark 隐藏答案的材料。
7. 任务实例、split 或原始数据确实属于论文方法且有助于理解或复现时可以纳入；在 `snapshot_scope` 中如实说明保留内容、用途与范围。`benchmark_leakage_check` 如存在，也必须依据实际文件填写。
8. 不在来源包文档中记录对本地文件计算的 MD5、SHA 或 checksum；`official_code_version.upstream_revision` 记录的官方 Git revision 不受此限制。

## 已收录来源

| 论文 | 方向 | 来源包 |
| --- | --- | --- |
| How Well Do Agentic Skills Work in the Wild: Benchmarking LLM Skill Usage in Realistic Settings | 指令与 Skill | [skill-usage-2604.04323](skill-usage-2604.04323/) |
| Inducing Programmatic Skills for Agentic Tasks | 指令与 Skill | [agent-skill-induction-2504.06821](agent-skill-induction-2504.06821/) |
| ACON: Optimizing Context Compression for Long-horizon LLM Agents | 上下文管理与压缩 | [acon-2510.00615](acon-2510.00615/) |
| AgentFold: Long-Horizon Web Agents with Proactive Context Management | 上下文管理与压缩 | [agentfold-2510.24699](agentfold-2510.24699/) |
| FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance | 模型选择与资源分配 | [frugalgpt-2305.05176](frugalgpt-2305.05176/) |
| RouteLLM: Learning to Route LLMs with Preference Data | 模型选择与资源分配 | [routellm-2406.18665](routellm-2406.18665/) |
| ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities | 工具与环境交互 | [toolsandbox-2025.findings-naacl.65](toolsandbox-2025.findings-naacl.65/) |
| The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models | 工具与环境交互 | [bfcl-2025.icml](bfcl-2025.icml/) |
| Why Do Multi-Agent LLM Systems Fail? | 容错与故障恢复 | [mast-2025.neurips](mast-2025.neurips/) |
| AgentDiagnose: An Open Toolkit for Diagnosing LLM Agent Trajectories | 容错与故障恢复 | [agentdiagnose-2025.emnlp-demos](agentdiagnose-2025.emnlp-demos/) |
| Open Grounded Planning: Challenges and Benchmark Construction | 执行循环与调度 | [open-grounded-planning-2024.acl-long.272](open-grounded-planning-2024.acl-long.272/) |
| HiAgent: Hierarchical Working Memory Management for Solving Long-Horizon Agent Tasks with Large Language Model | 执行循环与调度 | [hiagent-2025.acl-long](hiagent-2025.acl-long/) |
| AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework | 子 Agent 与多 Agent 协作 | [autogen-2308.08155](autogen-2308.08155/) |
| MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework | 子 Agent 与多 Agent 协作 | [metagpt-2308.00352](metagpt-2308.00352/) |
| SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering | 运行观测、Trace 与集成接口 | [swe-agent-2405.15793](swe-agent-2405.15793/) |
| OpenHands: An Open Platform for AI Software Developers as Generalist Agents | 运行观测、Trace 与集成接口 | [openhands-2407.16741](openhands-2407.16741/) |
| AgentRewind | 会话与环境状态管理 | [agentrewind-2608.14380](agentrewind-2608.14380/) |
| AgentScope | 扩展机制与生命周期钩子 | [agentscope-2508.16279](agentscope-2508.16279/) |
| ExpeL | 长期记忆与经验复用 | [expel-2308.10144](expel-2308.10144/) |
| NORA | 扩展机制与生命周期钩子 | [nora-2605.02092](nora-2605.02092/) |
| ReasoningBank | 长期记忆与经验复用 | [reasoningbank-2509.25140](reasoningbank-2509.25140/) |
| StateFork | 会话与环境状态管理 | [statefork-2609.38648](statefork-2609.38648/) |


## 近两年顶会与官方代码来源包

| 论文 | 录用 | 覆盖方向 | 来源包 |
| --- | --- | --- | --- |
| MAGIC: Generating Self-Correction Guideline for In-Context Text-to-SQL | AAAI 2025 | 指令与 Skill、长期记忆与经验复用、容错与故障恢复、执行循环与调度、规划与任务进度管理 | [magic-2406.12692](magic-2406.12692/) |
| ICL-Router: In-Context Learned Model Representations for LLM Routing | AAAI 2026 | 模型选择与资源分配 | [icl-router-2510.09719](icl-router-2510.09719/) |
| LLM Collaboration with Multi-Agent Reinforcement Learning | AAAI 2026 | 规划与任务进度管理、会话与环境状态管理、子 Agent 与多 Agent 协作 | [comlrl-2508.04652](comlrl-2508.04652/) |
| 500xCompressor: Generalized Prompt Compression for Large Language Models | ACL 2025 | 指令与 Skill、上下文管理与压缩 | [500xcompressor-2408.03094](500xcompressor-2408.03094/) |
| Agent-RewardBench: Towards a Unified Benchmark for Reward Modeling across Perception, Planning, and Safety in Real-World Multimodal Agents | ACL 2025 | 权限、审批与运行隔离、验证、评估与反馈 | [agent-rewardbench-2506.21252](agent-rewardbench-2506.21252/) |
| AgentDropout: Dynamic Agent Elimination for Token-Efficient and High-Performance LLM-Based Multi-Agent Collaboration | ACL 2025 | 指令与 Skill、上下文管理与压缩、执行循环与调度、规划与任务进度管理、模型选择与资源分配、子 Agent 与多 Agent 协作、扩展机制与生命周期钩子 | [agentdropout-2503.18891](agentdropout-2503.18891/) |
| DAC: A Dynamic Attention-aware Approach for Task-Agnostic Prompt Compression | ACL 2025 | 上下文管理与压缩 | [dac-2507.11942](dac-2507.11942/) |
| IRT-Router: Effective and Interpretable Multi-LLM Routing via Item Response Theory | ACL 2025 | 模型选择与资源分配 | [irt-router-2506.01048](irt-router-2506.01048/) |
| LLM Agents Making Agent Tools | ACL 2025 | 指令与 Skill、工具与环境交互、执行循环与调度、扩展机制与生命周期钩子 | [toolmaker-2502.11705](toolmaker-2502.11705/) |
| MasRouter: Learning to Route LLMs for Multi-Agent Systems | ACL 2025 | 模型选择与资源分配、子 Agent 与多 Agent 协作、扩展机制与生命周期钩子 | [masrouter-2502.11133](masrouter-2502.11133/) |
| MultiAgentBench : Evaluating the Collaboration and Competition of LLM agents | ACL 2025 | 执行循环与调度、规划与任务进度管理、会话与环境状态管理、子 Agent 与多 Agent 协作、扩展机制与生命周期钩子、运行观测、Trace 与集成接口、验证、评估与反馈 | [multiagentbench-2503.01935](multiagentbench-2503.01935/) |
| On the Limit of Language Models as Planning Formalizers | ACL 2025 | 规划与任务进度管理 | [llm-planning-formalizers-2412.09879](llm-planning-formalizers-2412.09879/) |
| INFERENCEDYNAMICS: Efficient Routing Across LLMs through Structured Capability and Knowledge Profiling | ACL 2026 | 指令与 Skill、模型选择与资源分配 | [inference-dynamics-2505.16303](inference-dynamics-2505.16303/) |
| Interactive Debugging and Steering of Multi-Agent AI Systems | CHI 2025 | 长期记忆与经验复用、容错与故障恢复、会话与环境状态管理、子 Agent 与多 Agent 协作、扩展机制与生命周期钩子、运行观测、Trace 与集成接口 | [agdebugger-2503.02068](agdebugger-2503.02068/) |
| Collab-Overcooked: Benchmarking and Evaluating Large Language Models as Collaborative Agents | EMNLP 2025 | 长期记忆与经验复用、子 Agent 与多 Agent 协作、验证、评估与反馈 | [collab-overcooked-2502.20073](collab-overcooked-2502.20073/) |
| GuardAgent: Safeguard LLM Agents via Knowledge-Enabled Reasoning | ICML 2025 | 指令与 Skill、工具与环境交互、长期记忆与经验复用、容错与故障恢复、规划与任务进度管理、权限、审批与运行隔离 | [guardagent-2406.09187](guardagent-2406.09187/) |
| Advancing Tool-Augmented Large Language Models via Meta-Verification and Reflection Learning | KDD 2025 | 指令与 Skill、工具与环境交互、执行循环与调度、运行观测、Trace 与集成接口 | [tool-mvr-2506.04625](tool-mvr-2506.04625/) |
| GUI-Robust: A Comprehensive Dataset for Testing GUI Agent Robustness in Real-World Anomalies | KDD 2026 | 工具与环境交互、上下文管理与压缩、容错与故障恢复、会话与环境状态管理、权限、审批与运行隔离、运行观测、Trace 与集成接口 | [gui-robust-2506.14477](gui-robust-2506.14477/) |
| Thought-Augmented Planning for LLM-Powered Interactive Recommender Agent | KDD 2026 | 长期记忆与经验复用、规划与任务进度管理 | [taira-2506.23485](taira-2506.23485/) |
| AgentSense: Benchmarking Social Intelligence of Language Agents through Interactive Scenarios | NAACL 2025 | 长期记忆与经验复用、子 Agent 与多 Agent 协作、验证、评估与反馈 | [agentsense-2410.19346](agentsense-2410.19346/) |
| Benchmarking Failures in Tool-Augmented Language Models | NAACL 2025 | 工具与环境交互、容错与故障恢复、权限、审批与运行隔离、运行观测、Trace 与集成接口、验证、评估与反馈 | [fail-talms-2503.14227](fail-talms-2503.14227/) |
| EASYTOOL: Enhancing LLM-based Agents with Concise Tool Instruction | NAACL 2025 | 指令与 Skill、工具与环境交互、上下文管理与压缩、扩展机制与生命周期钩子 | [easytool-2401.06201](easytool-2401.06201/) |
| Hello Again! LLM-powered Personalized Agent for Long-term Dialogue | NAACL 2025 | 上下文管理与压缩、长期记忆与经验复用、会话与环境状态管理 | [hello-again-2406.05925](hello-again-2406.05925/) |
| Revealing the Barriers of Language Agents in Planning | NAACL 2025 | 规划与任务进度管理 | [agent-planning-barriers-2410.12409](agent-planning-barriers-2410.12409/) |
| AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents | NeurIPS 2024 | 工具与环境交互、容错与故障恢复、执行循环与调度、会话与环境状态管理、权限、审批与运行隔离、扩展机制与生命周期钩子、运行观测、Trace 与集成接口、验证、评估与反馈 | [agentdojo-2406.13352](agentdojo-2406.13352/) |
| SGLang: Efficient Execution of Structured Language Model Programs | NeurIPS 2024 | 上下文管理与压缩、执行循环与调度、模型选择与资源分配、扩展机制与生命周期钩子 | [sglang-2312.07104](sglang-2312.07104/) |
| Smoothie: Label Free Language Model Routing | NeurIPS 2024 | 模型选择与资源分配 | [smoothie-2412.04692](smoothie-2412.04692/) |
| AgentAuditor: Human-Level Safety and Security Evaluation for LLM Agents | NeurIPS 2025 | 工具与环境交互、长期记忆与经验复用、子 Agent 与多 Agent 协作、权限、审批与运行隔离、运行观测、Trace 与集成接口、验证、评估与反馈 | [agentauditor-2506.00641](agentauditor-2506.00641/) |
| AgentDAM: Privacy Leakage Evaluation for Autonomous Web Agents | NeurIPS 2025 | 权限、审批与运行隔离、验证、评估与反馈 | [agentdam-2503.09780](agentdam-2503.09780/) |
| DRIFT: Dynamic Rule-Based Defense with Injection Isolation for Securing LLM Agents | NeurIPS 2025 | 工具与环境交互、容错与故障恢复、会话与环境状态管理、权限、审批与运行隔离 | [drift-2506.12104](drift-2506.12104/) |
| G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems | NeurIPS 2025 | 指令与 Skill、上下文管理与压缩、长期记忆与经验复用、执行循环与调度、规划与任务进度管理、会话与环境状态管理、子 Agent 与多 Agent 协作、扩展机制与生命周期钩子、运行观测、Trace 与集成接口 | [g-memory-2506.07398](g-memory-2506.07398/) |
| Lookahead Routing for Large Language Models | NeurIPS 2025 | 模型选择与资源分配 | [lookahead-routing-2510.19506](lookahead-routing-2510.19506/) |
| MESS+: Dynamically Learned Inference-Time LLM Routing in Model Zoos with Service Level Guarantees | NeurIPS 2025 | 执行循环与调度、模型选择与资源分配 | [mess-plus-2505.19947](mess-plus-2505.19947/) |
| OS-Harm: A Benchmark for Measuring Safety of Computer Use Agents | NeurIPS 2025 | 容错与故障恢复、权限、审批与运行隔离、验证、评估与反馈 | [os-harm-2506.14866](os-harm-2506.14866/) |
| RAGRouter: Learning to Route Queries to Multiple Retrieval-Augmented Language Models | NeurIPS 2025 | 上下文管理与压缩、模型选择与资源分配 | [ragrouter-2505.23052](ragrouter-2505.23052/) |
| SiriuS: Self-improving Multi-agent Systems via Bootstrapped Reasoning | NeurIPS 2025 | 指令与 Skill、上下文管理与压缩、长期记忆与经验复用、容错与故障恢复、执行循环与调度、规划与任务进度管理、会话与环境状态管理、子 Agent 与多 Agent 协作、扩展机制与生命周期钩子、运行观测、Trace 与集成接口 | [sirius-2502.04780](sirius-2502.04780/) |
| WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks | NeurIPS 2025 | 工具与环境交互、容错与故障恢复、会话与环境状态管理、权限、审批与运行隔离、运行观测、Trace 与集成接口、验证、评估与反馈 | [wasp-2504.18575](wasp-2504.18575/) |

## 李永康来源包机制索引

| 来源 | 提取的机制 | 机制与边界 | 逐条证据 |
| --- | --- | --- | --- |
| ReasoningBank | 成败推理经验提取与检索 | [说明](reasoningbank-2509.25140/mechanism-and-boundaries.md) | [映射](reasoningbank-2509.25140/claim-evidence-map.json) |
| ExpeL | 规则维护与成功示例检索 | [说明](expel-2308.10144/mechanism-and-boundaries.md) | [映射](expel-2308.10144/claim-evidence-map.json) |
| AgentRewind | 对齐上下文与工作区恢复 | [说明](agentrewind-2608.14380/mechanism-and-boundaries.md) | [映射](agentrewind-2608.14380/claim-evidence-map.json) |
| StateFork | 逻辑分支与物理状态分离 | [说明](statefork-2609.38648/mechanism-and-boundaries.md) | [映射](statefork-2609.38648/claim-evidence-map.json) |
| AgentScope | 生命周期回调输入输出合同 | [说明](agentscope-2508.16279/mechanism-and-boundaries.md) | [映射](agentscope-2508.16279/claim-evidence-map.json) |
| NORA | 宿主事件与结构化交接 | [说明](nora-2605.02092/mechanism-and-boundaries.md) | [映射](nora-2605.02092/claim-evidence-map.json) |
