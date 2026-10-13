# FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance

| 内容 | 位置 |
| --- | --- |
| 来源元数据 | [source-packet.json](source-packet.json) |
| 论文 v1 | [paper/paper-v1.pdf](paper/paper-v1.pdf) · [文本](paper/paper-v1.txt) |
| 官方核心代码 | [`official-code/`](official-code/)（`src/FrugalGPT/llmcascade.py` 与 `optimizer.py`） |
| 论文与代码定位 | [exact-source-anchors.md](exact-source-anchors.md) |
| 配置和运行入口 | [configs-and-examples.md](configs-and-examples.md) |
| 测试与论文结果 | [tests-and-reported-results.md](tests-and-reported-results.md) |

## 这篇论文解决什么

论文先把「用 LLM」的降本手段归纳为三类：**prompt adaptation**（换更短/更合适的提示）、
**LLM approximation**（缓存或微调小模型去逼近大模型）、**LLM cascade**（按序调用多个模型，
用打分函数决定是否升级到更强的模型）。FrugalGPT 是 cascade 的一个具体实例：用回归式打分函数
（如 DistilBERT）判断小模型的答案是否够用，不够才调用下一个模型。

与我们 harness 的关系：这是「模型选择与资源分配」方向的第一个来源，提供的是
**成本—质量权衡的协议与打分器训练方式**，不是可以直接搬进执行 harness 的提示技巧。

## 快照状态

`official-code/` 已入库，固定 revision `2b23e6acbd4b39f71912816640dcc59e45aa4b5e`（2026-10-13 取得）。
**明确缺失与过时项**：

- 纳入 `summary/`（作者实验结果 CSV/XLSX）、`src/visualize/visualize_tradeoffs_newmodels.ipynb`
  （复现论文 cost-performance 权衡图）与 `figures/`；仅未纳入 `data/`（约 13 MB 第三方公开数据集，
  可按上游说明重新下载）与运行缓存。
- 论文表 1 的 12 个商业 API 与其价格是 2023 年状态；`config/serviceinfo.json` 需按当前价格重填，
  **不能直接沿用论文里的成本数字**。
- 复跑需要多家供应商的 API 凭据（只走本地环境变量或本地配置文件，不入库）。
- 上游未提供单元测试目录，测试入口记为未知。

## 与本地实验的关系

本包只保存论文与官方代码，不含本地运行结果。方法实现（Method）尚未分配，本阶段不做本地 demo。
要在本 harness 生效，还需共同协议放开单一执行模型。
