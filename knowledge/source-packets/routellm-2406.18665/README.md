# RouteLLM: Learning to Route LLMs with Preference Data

| 内容 | 位置 |
| --- | --- |
| 来源元数据 | [source-packet.json](source-packet.json) |
| 论文 v1 | [paper/paper-v1.pdf](paper/paper-v1.pdf) · [文本](paper/paper-v1.txt) |
| 官方核心代码 | [`official-code/`](official-code/)（`routellm/controller.py`、`calibrate_threshold.py`、`routers/`） |
| 论文与代码定位 | [exact-source-anchors.md](exact-source-anchors.md) |
| 配置和运行入口 | [configs-and-examples.md](configs-and-examples.md) |
| 测试与论文结果 | [tests-and-reported-results.md](tests-and-reported-results.md) |

## 这篇论文解决什么

给定一个「强模型 + 弱模型」对，训练一个**路由器**在推理时逐请求决定用哪个模型：用人类偏好
数据（Chatbot Arena 对战）训练四种路由器（相似度加权 SW Ranking、矩阵分解 MF、BERT 分类器、
因果语言模型），并做数据增强。每个请求带一个**成本阈值**，阈值决定有多少比例的请求会走强模型，
因此可以在「质量—成本」曲线上取点，而不是固定一个折中。

与我们 harness 的关系：这是「模型选择与资源分配」方向的第二个来源。它的关键迁移点是
**用偏好数据校准阈值**这一套协议；FrugalGPT 的 cascade 是「顺序调用 + 打分升级」，RouteLLM 是
「单次二选一 + 成本阈值」，两者是同一问题的不同取舍。

## 快照状态

`official-code/` 已入库，固定 revision `0b64fdafe049e596a3f5657c219329f24af24198`（2026-10-13 取得）。
**明确缺失**：

- 路由器 checkpoint 在 HuggingFace（`routellm/mf_gpt4_augmented` 等，见 `config.example.yaml`），
  本快照**不含权重**，首次运行会从网络拉取。
- 未纳入 `routellm/evals/{gsm8k,mmlu,mt_bench}` 的评测数据与 `benchmarks/`、`assets/`。
- 运行需要强弱两个模型供应商的凭据（只走环境变量，不入库）。
- 上游未提供单元测试目录，测试入口记为未知。

## 与本地实验的关系

本包只保存论文与官方代码。本地对「按成本预算校准阈值、再按阈值路由」的机制级自测在
[`reproductions/zhouMF/method-reproduction/preference-based-llm-routing/`](../../../reproductions/zhouMF/method-reproduction/preference-based-llm-routing/)，用的是合成开发集与
占位打分器，不构成对论文数值的复现；要在本 harness 生效，还需共同协议放开单一执行模型。
