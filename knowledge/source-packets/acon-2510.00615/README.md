# ACON: Optimizing Context Compression for Long-horizon LLM Agents

| 内容 | 位置 |
| --- | --- |
| 来源元数据 | [source-packet.json](source-packet.json) |
| 论文 v3 | [paper/paper-v3.pdf](paper/paper-v3.pdf) · [文本](paper/paper-v3.txt) |
| 官方核心代码 | [`official-code/`](official-code/)（`src/productive_agents/ctxopt/` 与 `experiments/`） |
| 论文与代码定位 | [exact-source-anchors.md](exact-source-anchors.md) |
| 配置和运行入口 | [configs-and-examples.md](configs-and-examples.md) |
| 测试与论文结果 | [tests-and-reported-results.md](tests-and-reported-results.md) |

## 这篇论文解决什么

长程 agent 的观察与历史会无界增长，带来推理显存成本与「无关信息导致的推理退化」两个瓶颈。
ACON 把**观察压缩**与**历史压缩**统一到一个框架里，并在自然语言空间迭代优化压缩指南
（依据 agent 的失败分析），再把优化后的压缩器蒸馏进小模型，全程不更新被测模型参数。

对我们 harness 的价值：它是「上下文压缩」方向的第二个来源，与 AgentFold 的折叠机制互补
（ACON 压缩已有上下文，AgentFold 主动管理状态摘要）。

## 快照状态

`official-code/` 已入库，固定 revision `d63f9ae18959dc7215ff62899c94c5e8c56847ae`
（2026-10-13 取得，见 `source-packet.json` 的 `snapshot_scope`）。

- 未纳入：`assets/`（图片）与 `experiments/officebench/`（约 26 MB 数据）。
- 仓库自带 `configs/private_config_dummy.yaml` 只有占位键 `openai_key: <YOUR_OPENAI_KEY_HERE>`；
  运行前需自建 `configs/private_config.yaml` 并只通过本地文件注入凭据，凭据不入库。
- 上游**未提供单元测试目录**，`tests-and-reported-results.md` 的「测试入口」因此记为未知。

## 与本地实验的关系

本包只保存论文与官方代码，不含本地运行结果。本地对「压缩后关键事实是否丢失」的机制级
自测在 [`reproductions/zhouMF/method-reproduction/acon-context-compression/`](../../../reproductions/zhouMF/method-reproduction/acon-context-compression/)，不构成对论文数值的复现。
