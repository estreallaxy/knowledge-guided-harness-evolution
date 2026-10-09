# AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework

| 项目 | 固定材料 |
| --- | --- |
| 论文 | Qingyun Wu, Gagan Bansal, Jieyu Zhang 等（Microsoft Research 等），*AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework*，arXiv:2308.08155（v1 2023-08-16；v2 2023-10-03；暂固定 v2，是否为 arXiv 最新版本待联网复核），COLM 2024 正式发表。 |
| 本地 PDF | [`paper-v2.pdf`](paper-v2.pdf)  |
| 在线版本 | [摘要](https://arxiv.org/abs/2308.08155)；[OpenReview forum](https://openreview.net/forum?id=BakY1hNKS) |
| 代码 | [`microsoft/autogen`](https://github.com/microsoft/autogen)（MIT；v0.4 起重构为 event-driven actor 架构） |
| 收集与核对日期 | 2026-10-05 收集；发表状态按官方文档 Research 页的 COLM 2024 BibTeX 与 OpenReview forum 核对。 |

**机制摘要**：把任意 LLM 应用统一为「多个可对话 agent 自动交换消息」的单一范式。三个编排原语：(1) `ConversableAgent` 的 auto-reply 机制，收到消息即自动触发回复，形成对话驱动的控制流（即执行循环本身）；(2) `GroupChatManager` 动态选择下一位发言者，即协调者模式；(3) nested chat 允许 agent 在处理子任务时递归开启一段嵌套会话并回收结果，即子 agent 派发。ALFWorld 三 agent 系统 69.0% 成功率，显著超过单 agent 与 LangChain ReAct 基线。

**与本方向（子 Agent 与多 Agent 协作）的关联**：三个原语分别对应 harness 的执行循环、编排器（发言者选择策略可被知识引导替换）与子 agent 委派模块，是编排层公共词汇表的正式文献来源。

**本知识库提取的机制**：[Nested Subagent Delegation](../../methods/nested-subagent-delegation/README.md)（auto-reply / 发言者选择 / nested chat 子任务委派）。

本目录保存原始材料，不随本地实验结论改写。
