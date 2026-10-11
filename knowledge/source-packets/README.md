# Source Packets

每篇论文使用一个独立目录，目录名采用 `<短标题>-<arXiv编号或其他稳定标识>`。五位成员可以并行新增目录，不在这里保存某条 Method 的派生表示。

每个来源包必须包含：

```text
<paper-id>/
├── source-packet.json
├── paper/
│   ├── paper-vN.pdf
│   └── paper-vN.txt
├── official-code/
├── exact-source-anchors.md
├── configs-and-examples.md
└── tests-and-reported-results.md
```

| `SourcePacket` 字段 | 必须记录的内容 |
| --- | --- |
| `paper_version` | 论文题目、作者、版本、发布日期、来源 URL、本地 PDF 与文本路径。 |
| `official_code_version` | 官方仓库、固定上游 revision、获取日期、本地代码范围及许可证状态。 |
| `exact_source_anchors` | 每条机制、条件和限制在论文页码、章节、图表及代码文件中的精确位置。 |
| `configs_and_examples` | 论文或官方仓库实际使用的配置、命令、数据入口和运行前提。 |
| `tests_and_reported_results` | 官方测试入口、论文报告结果、消融、失败条件及本地复核状态。 |

收集时遵守以下规则：

1. 原始来源与后续 Method 派生物分开；来源包不提前写入某条路线的对象结构。
2. 论文与官方代码版本不能使用“最新版”代替；更新时新增版本记录，不覆盖旧材料。
3. 论文报告、代码实际行为和本地运行结果分别记录，缺失信息写明未知。
4. 不提交密钥、运行缓存、大型外部数据集或由 benchmark 泄露的测试答案。
5. 同一论文目录由提交者在合并前负责消解冲突；不同论文目录可以并行新增。

## 已收录来源

| 论文 | 方向 | 来源包 |
| --- | --- | --- |
| How Well Do Agentic Skills Work in the Wild: Benchmarking LLM Skill Usage in Realistic Settings | 指令与 Skill | [skill-usage-2604.04323](skill-usage-2604.04323/) |
