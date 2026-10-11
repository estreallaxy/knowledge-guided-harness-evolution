# Why Do Multi-Agent LLM Systems Fail?

| 内容 | 位置 |
| --- | --- |
| 来源元数据 | [source-packet.json](source-packet.json) |
| 论文 v1 | [paper/paper-v1.pdf](paper/paper-v1.pdf) · [文本](paper/paper-v1.txt) |
| 官方核心代码 | [official-code/](official-code/) |
| 论文与代码定位 | [exact-source-anchors.md](exact-source-anchors.md) |
| 配置和运行入口 | [configs-and-examples.md](configs-and-examples.md) |
| 测试与论文结果 | [tests-and-reported-results.md](tests-and-reported-results.md) |

论文由 NeurIPS 2025 Datasets and Benchmarks Track 正式发表（DOI 10.52202/085713-4082），来源为其官方 proceedings PDF，按文本页码标记共 54 页（正文 10 页 + 参考文献 + 附录 A–N）。核心产出是 MAST 失败分类法（14 个失败模式 / 3 个大类）、MAST-Data 标注数据集（1642 条 trace），以及把 MAST 用于大规模标注的 LLM-as-a-Judge 流水线。
