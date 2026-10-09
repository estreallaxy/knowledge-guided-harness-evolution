# OpenHands: An Open Platform for AI Software Developers as Generalist Agents

| 项目 | 固定材料 |
| --- | --- |
| 论文 | Xingyao Wang, Boxuan Li, Yufan Song, Frank F. Xu 等（All Hands AI / CMU / UIUC 等，含 Graham Neubig），*OpenHands: An Open Platform for AI Software Developers as Generalist Agents*，arXiv:2407.16741（v1 2024-07；v3 2025-04-18），ICLR 2025 主会。 |
| 本地 PDF | [`paper-v3.pdf`](paper-v3.pdf)  |
| 在线版本 | [摘要](https://arxiv.org/abs/2407.16741)；[ICLR 官方论文集](https://proceedings.iclr.cc/paper_files/paper/2025/hash/a4b6ad6b48850c0c331d1259fc66a69c-Abstract-Conference.html)；[OpenReview](https://openreview.net/forum?id=O1d3ayDDoF) |
| 代码 | [`All-Hands-AI/OpenHands`](https://github.com/All-Hands-AI/OpenHands)（MIT，约 8.9 万 star，社区贡献 2K+ 提交） |
| 收集与核对日期 | 2026-10-05 收集；发表状态按 ICLR 2025 官方论文集 BibTeX 与 OpenReview forum 核对。 |

**机制摘要**：完整的开源软件 agent 平台，三大组件：(1) agenthub——统一的 agent 抽象与注册机制；(2) event stream——以 Action/Observation 事件流统一 agent、环境与 UI 之间的所有通信，天然形成结构化、可逐步回放与评估的执行轨迹；(3) runtime——在 Docker sandbox 中执行 IPythonRunCellAction、CmdRunAction、BrowserInteractiveAction 等动作。默认 CodeAct agent 把可执行 Python 代码作为统一动作空间。平台在 SWE-bench、WebArena 等 15 项任务上验证。

**与本方向（运行观测、Trace 与集成接口）的关联**：event stream 即运行观测层的结构化轨迹基础设施，动作抽象即环境集成接口规范——是日志采集、重放调试、轨迹分析的可直接借鉴蓝本；动作分类（代码/命令/浏览）同时是接口设计规范。

**本知识库提取的机制**：[Action-Observation Event Stream](../../methods/action-observation-event-stream/README.md)（统一事件流、嵌套事件、过滤/回放/JSONL 导出）。

本目录保存原始材料，不随本地实验结论改写。
