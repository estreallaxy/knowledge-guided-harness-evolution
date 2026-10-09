# 实验依据

以下数值已对照本地 PDF（paper-v2.pdf，arXiv:2308.08155v2，COLM 2024）逐项复核。

| 实验 | 结果 |
| --- | --- |
| ALFWorld 三 agent 系统 | ALFChat（3 agents）全部任务成功率 69%（两 agent 版 54%；ReAct 基线 54%；best-of-3 77% vs 66%）；引入 grounding agent 平均提升 15%（134 道未见题） |
| MATH 总成功率 | 69.48%（GPT-4 直答 55.18%） |
| 覆盖场景 | 数学、检索增强、决策（ALFWorld）、多 agent 编码、动态群聊等 |

## 证据限制

- 论文为框架论文，经验验证深度一般；以上为框架展示性实验，无与 H0 相同设置的对照。
- v0.4 起重构为 event-driven actor 架构，论文描述的 API 与现行实现已有差异；复现前需对照上游仓库当前版本。
- 不能引用为「子 agent 委派在 Terminus-KIRA 上有效」。
