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

## 已收录来源

| 论文 | 方向 | 来源包 |
| --- | --- | --- |
| How Well Do Agentic Skills Work in the Wild: Benchmarking LLM Skill Usage in Realistic Settings | 指令与 Skill | [skill-usage-2604.04323](skill-usage-2604.04323/) |
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


## 李永康来源包机制索引

| 来源 | 提取的机制 | 机制与边界 | 逐条证据 |
| --- | --- | --- | --- |
| ReasoningBank | 成败推理经验提取与检索 | [说明](reasoningbank-2509.25140/mechanism-and-boundaries.md) | [映射](reasoningbank-2509.25140/claim-evidence-map.json) |
| ExpeL | 规则维护与成功示例检索 | [说明](expel-2308.10144/mechanism-and-boundaries.md) | [映射](expel-2308.10144/claim-evidence-map.json) |
| AgentRewind | 对齐上下文与工作区恢复 | [说明](agentrewind-2608.14380/mechanism-and-boundaries.md) | [映射](agentrewind-2608.14380/claim-evidence-map.json) |
| StateFork | 逻辑分支与物理状态分离 | [说明](statefork-2609.38648/mechanism-and-boundaries.md) | [映射](statefork-2609.38648/claim-evidence-map.json) |
| AgentScope | 生命周期回调输入输出合同 | [说明](agentscope-2508.16279/mechanism-and-boundaries.md) | [映射](agentscope-2508.16279/claim-evidence-map.json) |
| NORA | 宿主事件与结构化交接 | [说明](nora-2605.02092/mechanism-and-boundaries.md) | [映射](nora-2605.02092/claim-evidence-map.json) |
