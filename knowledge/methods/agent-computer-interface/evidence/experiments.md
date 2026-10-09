# 实验依据

以下数值已对照本地 PDF（paper-v3.pdf，arXiv:2405.15793v3，NeurIPS 2024）逐项复核。

| 实验 | 结果 |
| --- | --- |
| SWE-bench 解决率 | 12.47%（摘要作 12.5%）pass@1，共 2,294 题；此前最佳非交互式检索基线 3.8% |
| HumanEvalFix | 87.7% pass@1（GPT-4 Turbo） |
| ACI 消融（SWE-bench Lite 300 题） | 完整 ACI 比仅给 Linux shell 的基线多解决 10.7 个百分点 |
| 权重与可移植性 | 不修改任何模型权重，收益来自接口与反馈设计；接口收益可跨模型（Claude 3 Opus 上 10.5%） |

## 证据限制

- 完整 ACI 的消融对照在 SWE-bench Lite 子集上完成；窗口大小、反馈格式等参数的敏感性需对照论文 §5 与表 3 进一步整理。
- 与本项目 H0 的工具层和任务分布不同；不能直接引用为「ACI 在 Terminus-KIRA 上有效」。
- SWE-bench 上的 token 开销、单题时延与轨迹长度未逐项核对，需对照 PDF 与本地实验补充。
