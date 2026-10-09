# AFlow: Automating Agentic Workflow Generation

| 项目 | 固定材料 |
| --- | --- |
| 论文 | Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu 等（DeepWisdom，含 Mingchen Zhuge、Jürgen Schmidhuber），*AFlow: Automating Agentic Workflow Generation*，arXiv:2410.10762（v1 2024-10-14；v4 2025-04-15），ICLR 2025 正式论文集收录（代码仓库标注 Oral；官方站点 poster 列表与社区公告说法不一，如实记录）。 |
| 本地 PDF | [`paper-v4.pdf`](paper-v4.pdf) |
| 在线版本 | [摘要](https://arxiv.org/abs/2410.10762)；[ICLR 官方论文集 PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/5492ecbce4439401798dcd2c90be94cd-Paper-Conference.pdf)；[OpenReview](https://openreview.net/forum?id=z5uVAKwmjf) |
| 代码 | [`FoundationAgents/AFlow`](https://github.com/FoundationAgents/AFlow)（MIT，含完整 optimizer/evaluator/operator 代码与原始实验数据） |
| 收集与核对日期 | 2026-10-05 收集；发表状态按 ICLR 2025 官方论文集 PDF 与 OpenReview forum 核对。 |

**机制摘要**：把 agentic workflow 优化重构为「代码表示的 workflow 图空间上的搜索问题」——节点为带参数（模型、prompt、temperature、输出格式）的 LLM 调用，边为信息流；LLM 驱动的 MCTS（Optimizer）完成选择、展开、执行评估与经验回传，Evaluator 在六个 benchmark（HumanEval、MBPP、GSM8K、MATH、HotpotQA、DROP）上执行验证并返回反馈；预定义可复用 Operator（Generate/Format/Review/Revise/Ensemble/Test 等）约束搜索空间。较手工设计平均 +5.7%；发现的小模型 workflow 以 4.55% 推理成本超越 GPT-4o，且跨模型迁移保持 95.4% 性能。

**与本方向（验证、评估与反馈）的关联**：「修改 → 执行验证 → 反馈驱动下一步」闭环与 harness 优化几乎同构——Evaluator 对应 harness 验证器，Operator 库对应可复用构件，树结构经验对应验证记录与失败归因。

本目录保存原始材料，不随本地实验结论改写。
