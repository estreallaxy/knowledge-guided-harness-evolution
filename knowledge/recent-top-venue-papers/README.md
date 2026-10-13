# 近两年顶会论文池

> 收录范围为 2025–2026 年已进入正式 proceedings 的论文。每个方向 10 篇；同一论文可关联多个方向，但在 `manifest.json` 中只保留一条规范记录。该目录是进入 SourcePacket 制作流程前的已核验论文池，不替代论文精读、官方代码固定和精确锚点抽取。

| 方向 | 数量 | 清单 |
| --- | ---: | --- |
| 指令与 Skill | 10 | [instructions-and-skills.md](instructions-and-skills.md) |
| 工具与环境交互 | 10 | [tools-and-environments.md](tools-and-environments.md) |
| 上下文管理与压缩 | 10 | [context-management-and-compression.md](context-management-and-compression.md) |
| 长期记忆与经验复用 | 10 | [long-term-memory-and-experience-reuse.md](long-term-memory-and-experience-reuse.md) |
| 容错与故障恢复 | 10 | [fault-tolerance-and-recovery.md](fault-tolerance-and-recovery.md) |
| 执行循环与调度 | 10 | [execution-loop-and-scheduling.md](execution-loop-and-scheduling.md) |
| 规划与任务进度管理 | 10 | [planning-and-progress-management.md](planning-and-progress-management.md) |
| 模型选择与资源分配 | 10 | [model-selection-and-resource-allocation.md](model-selection-and-resource-allocation.md) |
| 会话与环境状态管理 | 10 | [session-and-environment-state.md](session-and-environment-state.md) |
| 子 Agent 与多 Agent 协作 | 10 | [subagents-and-multiagent-collaboration.md](subagents-and-multiagent-collaboration.md) |
| 权限、审批与运行隔离 | 10 | [permissions-approval-and-isolation.md](permissions-approval-and-isolation.md) |
| 扩展机制与生命周期钩子 | 10 | [extensions-and-lifecycle-hooks.md](extensions-and-lifecycle-hooks.md) |
| 运行观测、Trace 与集成接口 | 10 | [observability-traces-and-interfaces.md](observability-traces-and-interfaces.md) |
| 验证、评估与反馈 | 10 | [verification-evaluation-and-feedback.md](verification-evaluation-and-feedback.md) |

共 121 篇不重复论文、140 条方向关联。

## 纳入规则

1. 论文年份为 2025 或 2026。
2. 论文已出现在 ACL、NAACL、EMNLP、NeurIPS、ICML、AAAI、KDD、WWW 或 CHI 的正式 proceedings。
3. 排除 arXiv-only、workshop、Findings、tutorial、doctoral/SRW、extended abstract 和纯综述。
4. 与 `knowledge/source-packets/README.md` 的既有论文按标题去重。
5. 论文与方向必须存在可落到 Harness 组件或优化流程的机制联系；领域应用论文只有在提供可迁移机制时纳入。

## 后续处理

清单中的论文转为可调用知识前，仍需按照 [`source-packets/README.md`](../source-packets/README.md) 下载论文、固定官方代码版本、抽取精确来源锚点，并记录配置、测试、结果与适用边界。
