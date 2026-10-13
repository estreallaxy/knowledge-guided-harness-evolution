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
6. `official-code/` 只保存理解和复现机制所需的源码与轻量配置；排除 benchmark 任务实例、split、含参考答案或评分规则的测试配置、登录状态及原始数据。
7. `benchmark_leakage_check` 必须依据来源包实际包含的文件填写；未逐文件核对时写“未知”，不能直接声明无泄漏。
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
