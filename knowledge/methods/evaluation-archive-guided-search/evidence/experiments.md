# 实验依据

以下数值已对照本地 PDF（paper-v2.pdf，arXiv:2408.08435v2，ICLR 2025）逐项复核。

| 实验 | 结果 |
| --- | --- |
| DROP（阅读理解） | F1 提升 +13.6（原文 13.6/100 口径） |
| MGSM（数学） | 准确率提升 +14.4% |
| GSM8K / GSM-Hard（跨域迁移后） | +25.9% / +13.2% |
| 跨模型迁移 | GPT-3.5 上搜索出的 agent 迁移到 Claude-Haiku / GPT-4 / Claude-Sonnet 均保持优势（Claude-Sonnet 上最佳 agent 接近 50% ARC） |
| 对比基线 | 超过 Chain-of-Thought、Self-Refine、LLM Debate、COT-SC、Quality-Diversity 等手工设计 agent |

## 证据限制

- 论文的搜索与评估在领域任务（ARC、DROP、MGSM 等）上进行，不是 harness 修改任务；收益不能直接折算到本项目。
- 每轮搜索的模型调用、评估次数与总费用未逐项核对，成本核算待整理。
- 数值为论文自报的 test 表现（含 95% bootstrap 置信区间），与基线的统计口径需注意。
