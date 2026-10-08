# 方法知识索引

本页只用于快速找到可能适用的方法。进入方法页后即可判断是否采用；确定采用后直接运行随方法保存的代码。论文与核验材料不进入默认运行链路。

| 方法 | 解决的问题 | Harness 模块 | 使用前提 | 可运行代码 | 证据状态 | 方法页 |
| --- | --- | --- | --- | --- | --- | --- |
| Query-specific Skill Refinement | 候选 Skill 部分相关、含噪声或难以直接采用 | Skill 选择、适配与加载 | 候选 Skill 已覆盖核心知识；允许额外探索一次 | 已提供；尚未接入共同 H0 | 论文与固定代码已核对，本地代码待真实 Harbor 运行 | [查看](methods/query-specific-skill-refinement/README.md) |
| ToolSandbox | 有状态工具调用和多轮环境交互的评价 | 工具执行、状态管理、轨迹评价 | 任务存在工具间状态依赖；需要中间状态与最终状态评价 | 已收集；尚未接入共同 H0 | 正式会议论文和官方代码已固定；本地迁移未验证 | [查看](methods/toolsandbox/README.md) |
| BFCL | 函数调用、并行/串行调用和多轮 Agent 工具使用评价 | 工具选择、参数生成、调用编排 | 需要标准化工具调用基准或回归评价 | 已收集；尚未接入共同 H0 | 正式会议论文和官方代码已固定；本地迁移未验证 | [查看](methods/bfcl/README.md) |
| MAST | 多 Agent 系统的结构化失败模式分类 | 故障诊断、协作与终止 | 需要分析多 Agent 轨迹或系统故障 | 官方代码与数据已收集；尚未接入共同 H0 | 正式会议论文和官方代码已固定；本地迁移未验证 | [查看](methods/mast/README.md) |
| AgentDiagnose | 对 LLM Agent 轨迹进行诊断和回溯分析 | Trace 观测、失败定位、自验证 | 需要保存可分析的 Agent trajectory | 官方代码已收集；尚未接入共同 H0 | 正式会议论文和官方代码已固定；本地迁移未验证 | [查看](methods/agentdiagnose/README.md) |
| Open Grounded Planning | 规划、知识绑定与执行反馈 | 规划、工具调度、执行循环 | 任务需要外部知识和工具交互 | 官方代码已收集；尚未接入共同 H0 | ACL 2024 正式论文和官方代码已固定；本地迁移未验证 | [查看](methods/open-grounded-planning/README.md) |
| HiAgent | 长时域任务的分层工作记忆 | 长任务执行、上下文与记忆 | 任务可拆分为层级子任务 | 官方代码已收集；尚未接入共同 H0 | ACL 2025 正式论文和官方代码已固定；本地迁移未验证 | [查看](methods/hiagent/README.md) |
| R-Judge | Agent 安全风险识别与评价 | 风险回归、权限与安全观测 | 需要独立记录 Agent 安全风险 | 官方代码已收集；尚未接入共同 H0 | EMNLP Findings 2024 正式论文和官方代码已固定；本地迁移未验证 | [查看](methods/r-judge/README.md) |
| RedCode | 代码 Agent 执行风险与安全评测 | 运行隔离、权限边界、安全回归 | 任务涉及代码生成或代码执行 | 官方代码已收集；尚未接入共同 H0 | NeurIPS 2024 正式论文和官方代码已固定；本地迁移未验证 | [查看](methods/redcode/README.md) |
