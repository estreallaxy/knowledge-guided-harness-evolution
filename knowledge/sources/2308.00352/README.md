# MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

| 项目 | 固定材料 |
| --- | --- |
| 论文 | Sirui Hong, Mingchen Zhuge, Jonathan Chen 等（DeepWisdom / KAUST / UC Berkeley 等，含 Jürgen Schmidhuber），*MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework*，arXiv:2308.00352（v1 2023-08-01；v7 2024-11-01），ICLR 2024 **Oral**（接收率 top 1.2%，LLM-based Agent 类排名第一）。 |
| 本地 PDF | [`paper-v7.pdf`](paper-v7.pdf) |
| 在线版本 | [摘要](https://arxiv.org/abs/2308.00352)；[OpenReview](https://openreview.net/forum?id=VtmBAGCN7o)；[ICLR 官方论文集](https://proceedings.iclr.cc/paper_files/paper/2024/hash/6507b115562bb0a305f1958ccc87355a-Abstract-Conference.html) |
| 代码 | [`geekan/MetaGPT`](https://github.com/geekan/MetaGPT)（MIT，约 6.4 万 star） |
| 收集与核对日期 | 2026-10-05 收集；发表状态按 ICLR 2024 官方论文集页面与 OpenReview forum 核对。 |

**机制摘要**：把人类软件公司的 SOP（标准化作业流程）编码为角色流水线的 prompt 序列，按角色（产品经理→架构师→项目经理→工程师→QA）把复杂任务分解并委派给不同 agent；各角色产出结构化中间产物（PRD、设计文档、数据流图）而非自由聊天，抑制级联幻觉；agent 间通信采用发布-订阅消息池（只订阅自己角色的消息类型）；QA 运行生成的代码并按报错迭代修复。HumanEval 85.9% / MBPP 87.7% Pass@1 为当时 SOTA。

**与本方向（子 Agent 与多 Agent 协作）的关联**：SOP 模板即「知识引导的任务分解器」，消息池 pub-sub 即通信总线，QA 审查循环即执行反馈验证——三个机制均可独立抽取迁移；与本项目「知识引导的 harness 构建」主线直接呼应。

本目录保存原始材料，不随本地实验结论改写。
