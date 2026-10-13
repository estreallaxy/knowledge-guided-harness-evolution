# 实现依据

`code/context_compression.py` 实现了论文的「压缩指南迭代」闭环，压缩层与 agent 决策层分离：

| 论文环节 | 本仓库实现 | 说明 |
| --- | --- | --- |
| 超预算才压缩 | `compress_if_needed(history, guideline, budget, summarize)` | 历史未超预算时返回 `None`，不做无谓改动。 |
| 压缩为状态摘要 + 保留项 | `CompressionResult`（`summary` + `retained`） | 系统消息与 `guideline.retain_kinds` 命中的条目原样保留，其余折成一条摘要。 |
| 由失败反推 | `find_missing_facts` / `revise_guideline` | 只在「全量上下文成功、压缩上下文失败」的开发轨迹上找丢失事实，并据此加保留规则，规则记入 `Guideline.revisions`。 |
| 迭代到开发集无失败 | `_demo` 的多轮修订循环 | 每轮重新检查全部开发轨迹，最多 3 轮。 |
| 摘要器 | `default_summarizer(budget)` | 确定性、有字数上限的占位实现；论文是蒸馏出的压缩器，`summarize-live` 演示用模型替换。 |

**未实现（论文有、本地没有）**：训练/蒸馏压缩器、AppWorld/OfficeBench 的环境与判分、
以及论文报告的成功率变化。本地 demo 只检验机制自洽与压缩/保留的权衡。
