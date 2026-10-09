# Automated Design of Agentic Systems (ADAS)

| 项目 | 固定材料 |
| --- | --- |
| 论文 | Shengran Hu, Cong Lu, Jeff Clune（UBC / Vector Institute），*Automated Design of Agentic Systems*，arXiv:2408.08435（v1 2024-08-15；v2 2025-03-02），ICLR 2025 poster；另获 NeurIPS 2024 Open-World Agent Workshop Outstanding Paper。 |
| 本地 PDF | [`paper-v2.pdf`](paper-v2.pdf) |
| 在线版本 | [摘要](https://arxiv.org/abs/2408.08435)；[ICLR 官方 poster 页](https://iclr.cc/virtual/2025/poster/28073)；[ICLR 官方 slides](https://iclr.cc/media/iclr-2025/Slides/28073.pdf) |
| 代码 | [`ShengranHu/ADAS`](https://github.com/ShengranHu/ADAS)（官方实现，README 标注 ICLR 2025） |
| 收集与核对日期 | 2026-10-05 收集；发表状态按 ICLR 官方 poster 页与官方仓库标注核对。 |

**机制摘要**：提出 Automated Design of Agentic Systems（ADAS）研究域：agent 即代码，代码图灵完备，因此 agentic 系统设计可在代码空间中搜索。核心算法 Meta Agent Search：一个 meta agent（LLM）迭代地为新任务编写新 agent 代码；每次生成的设计在任务上评估打分，分数与设计一起存入不断增长的 archive，作为后续生成的启发素材（含自我反思与 error-repair 步骤）。发现的 agent 显著超过手工基线（DROP F1 +13.6；跨域迁移后 GSM8K +25.9%、GSM-Hard +13.2%），且跨任务域、跨模型（GPT-3.5→Claude-Sonnet）迁移后仍保持优势。

**与本方向（验证、评估与反馈）的关联**：archive-with-scores 是「验证一次修改是否有效」的最小实现——每个候选修改经任务评估产生量化分数并回流存档，反馈信号直接驱动下一轮搜索与 error-repair；该闭环可原样迁移为 harness 修改的验证与迭代器。

**本知识库提取的机制**：[Evaluation Archive Guided Search](../../methods/evaluation-archive-guided-search/README.md)（评分存档、成败样例检索与引导提示生成）。

本目录保存原始材料，不随本地实验结论改写。
