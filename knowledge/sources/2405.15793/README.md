# SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

| 项目 | 固定材料 |
| --- | --- |
| 论文 | John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, Ofir Press（Princeton / Stanford），*SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*，arXiv:2405.15793（v1 2024-05-06；v3 2024-11-11，NeurIPS camera-ready），NeurIPS 2024 主会（DOI 10.52202/079017-1601；ACM DL 10.5555/3737916.3739517；页码 50528–50652）。 |
| 本地 PDF | [`paper-v3.pdf`](paper-v3.pdf)  |
| 在线版本 | [摘要](https://arxiv.org/abs/2405.15793)；[NeurIPS 官方论文集](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html) |
| 代码 | [`princeton-nlp/SWE-agent`](https://github.com/princeton-nlp/SWE-agent)（MIT，约 1.9 万 star） |
| 收集与核对日期 | 2026-10-05 收集；发表状态按 NeurIPS 官方论文集页面与 DOI 核对。 |

**机制摘要**：首次明确提出 Agent-Computer Interface（ACI）概念——为 LM 特制「计算机接口」而非让人适应计算机。核心机制：窗口化文件查看器（每次显示 100 行、支持滚动与搜索）；edit 命令配 linter/语法 guardrail，语法错误的编辑自动回退；简洁而信息充分的执行反馈（如「命令成功运行且没有产生输出」）；全目录字符串搜索命令。不修改模型权重，SWE-bench 12.5% pass@1（当时 SOTA，RAG 基线 3.8%），HumanEvalFix 87.7%；消融显示完整 ACI 较裸 shell 提升约 10.7 个百分点。

**与本方向（运行观测、Trace 与集成接口）的关联**：接口与反馈格式是 harness 观测层与工具层的一等设计对象——命令集即可插拔工具槽，guardrails 即 step 级错误拦截钩子，配置文件即扩展注册机制，反馈信息量设计即观测契约。

本目录保存原始材料，不随本地实验结论改写。
