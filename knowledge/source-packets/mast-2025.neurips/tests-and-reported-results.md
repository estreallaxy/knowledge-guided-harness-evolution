# Tests and reported results

以下全部为**论文报告结果，不是本仓库复跑结果**。本来源包未执行任何论文实验。

## 分类法与标注器的一致性

| 指标 | 数值 | 位置 |
| --- | --- | --- |
| 三轮 IAA 的 Cohen's κ（每轮 3 名专家、5 条 trace，共约 10 小时讨论） | 0.88 | §3.2，PDF pp.5–6 |
| 在 OpenManus / Magentic-One 与 MMLU / GAIA 这组未参与分类法构建的额外一轮 IAA | κ = 0.79 | §3.4，PDF p.6 |

Table 2（PDF p.6）LLM-as-a-Judge 与人类专家的一致性，模型为 OpenAI o1：

| 设置 | Accuracy | Recall | Precision | F1 | Cohen's κ |
| --- | ---: | ---: | ---: | ---: | ---: |
| o1 | 0.89 | 0.62 | 0.68 | 0.64 | 0.58 |
| o1（few-shot） | 0.94 | 0.77 | 0.833 | 0.80 | 0.77 |

few-shot 是论文采用的配置；无 few-shot 时 κ 从 0.77 降到 0.58，说明定义与示例的注入是流水线成立的关键条件。

## 失败模式在 1642 条 trace 上的占比

数据来自 §4 正文，Figure 1（PDF p.2）为同一组数据的图示；Figure 1 与 §4 正文在 FM-2.4 上相差 0.05 个百分点。

| 类别 | 失败模式 | 占比 |
| --- | --- | ---: |
| FC1 System Design Issues（44.2%） | 1.1 Disobey Task Specification | 11.8% |
| | 1.2 Disobey Role Specification | 1.5% |
| | 1.3 Step Repetition | 15.7% |
| | 1.4 Loss of Conversation History | 2.80% |
| | 1.5 Unaware of Termination Conditions | 12.4% |
| FC2 Inter-Agent Misalignment（32.3%） | 2.1 Conversation Reset | 2.20% |
| | 2.2 Fail to Ask for Clarification | 6.80% |
| | 2.3 Task Derailment | 7.40% |
| | 2.4 Information Withholding | 0.85%（Figure 1 作 0.80%） |
| | 2.5 Ignored Other Agent's Input | 1.90% |
| | 2.6 Reasoning-Action Mismatch | 13.2% |
| FC3 Task Verification（23.5%） | 3.1 Premature Termination | 6.20% |
| | 3.2 No or Incomplete Verification | 8.20% |
| | 3.3 Incorrect Verification | 9.10% |

同一论文里另有两组不可与之混用的分布：Figure 2（PDF p.5）用于描述方法流程，给出 37.17% / 31.41% / 31.41%；Figure 4（PDF p.8）只统计 7 个系统各自的头 30 条 trace（共 210 条），给出 41.8% / 36.9% / 21.3%。

## 数据集配置

Table 1（PDF p.3）全部 18 行（HE = 人工评测任务完成度，HA = 人工标注失败模式，LA = LLM 标注）：

| MAS | Benchmark | LLM | 标注 | Trace 数 |
| --- | --- | --- | --- | ---: |
| MetaGPT | ProgramDev | GPT-4o | HE, HA, LA | 30 |
| ChatDev | ProgramDev | GPT-4o | HE, HA, LA | 30 |
| HyperAgent | SWE-Bench Lite | Claude-3.7-Sonnet | HE, HA, LA | 30 |
| AppWorld | Test-C | GPT-4o | HE, HA, LA | 30 |
| AG2 (MathChat) | GSM-Plus | GPT-4 | HE, HA, LA | 30 |
| Magentic-One | GAIA | GPT-4o | HE, HA, LA | 30 |
| OpenManus | ProgramDev | GPT-4o | HE, HA, LA | 30 |
| AG2 (MathChat) | OlympiadBench | GPT-4o | HE, LA | 206 |
| AG2 (MathChat) | GSMPlus | Claude-3.7-Sonnet | HE, LA | 193 |
| AG2 (MathChat) | MMLU | GPT-4o-mini | HE, LA | 168 |
| Magentic-One | GAIA | GPT-4o | HE, LA | 165 |
| ChatDev | ProgramDev-v2 | GPT-4o | LA | 100 |
| MetaGPT | ProgramDev-v2 | GPT-4o | LA | 100 |
| MetaGPT | ProgramDev-v2 | Claude-3.7-Sonnet | LA | 100 |
| ChatDev | ProgramDev-v2 | Qwen2.5-Coder-32B-Instruct | LA | 100 |
| MetaGPT | ProgramDev-v2 | Qwen2.5-Coder-32B-Instruct | LA | 100 |
| ChatDev | ProgramDev-v2 | CodeLlama-7b-Instruct-hf | LA | 100 |
| MetaGPT | ProgramDev-v2 | CodeLlama-7b-Instruct-hf | LA | 100 |

逐行相加为 1642，与论文自述的 trace 总数一致。Table 1 覆盖 7 个开源 MAS；闭源平台（如 Manus）因不提供完整执行 trace 未纳入标注，见 Appendix B.3。

## 干预案例研究的准确率

Table 5（PDF p.34），数值为百分数，AG2 列为 6 次重复的均值 ± 标准差：

| 配置 | AG2 / GSM-Plus（GPT-4） | AG2 / GSM-Plus（GPT-4o） | ChatDev / ProgramDev-v0 | ChatDev / HumanEval |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 84.75 ± 1.94 | 84.25 ± 1.86 | 25.0 | 89.6 |
| Improved prompt | 89.75 ± 1.44 | 89.00 ± 1.38 | 34.4 | 90.3 |
| New topology | 85.50 ± 1.18 | 88.83 ± 1.51 | 40.6 | 91.5 |

论文同时报告 Wilcoxon 检验：GPT-4 上 baseline 与改进的 p = 0.4（不显著），GPT-4o 上 p = 0.03（显著）。正文另有两处单独报告的收益：ChatDev 仅改角色规范 +9.4%（PDF p.3），加入高层目标验证 +15.6%（PDF p.8）。论文明确指出这些改进没有解决全部失败模式，任务完成率仍偏低。

## 其他论文报告量

| 项目 | 数值 | 位置 |
| --- | --- | --- |
| 类别间相关性 | 0.17–0.32 | Appendix E，Figure 6，PDF p.29 |
| 模式间最高相关性 | 0.63 | Appendix E，Figure 7，PDF p.29 |
| 标注平均 API 成本 | 全框架 1.8 美元；AppWorld 0.3740、HyperAgent 0.9695、AG2 1.1656、ChatDev 2.1272、MetaGPT 2.4455、MagenticOne 1.3056、OpenManus 4.1409 | Appendix K，Table 9，PDF p.37 |
| 闭源系统人工评测 | Manus 在 ProgramDev 上 60% 成功率 | Appendix B.3，PDF p.27 |

## 官方检查入口

官方仓库没有测试套件、CI 或断言脚本；可用的检查手段只有 notebook 内的自检输出：

| 检查对象 | 入口 |
| --- | --- |
| 答案解析是否失败 | `official-code/llm_judge_pipeline.ipynb:264`：解析不到某个模式的 yes/no 时打印 `Warning: Could not find mode ... in response ...` 并按 0 处理（整条解析异常则在 `:268` 打印并全置 0） |
| 分组是否对齐 | `official-code/llm_judge_pipeline.ipynb:335`：某来源取不到值时打印 `Warning: Source ... has no values for mode ...` |
| 逐模式占比 | `official-code/llm_judge_pipeline.ipynb:284-299` |
| 分类法定义是否覆盖全部模式 | 对照 `taxonomy_definitions_examples/definitions.txt` 与 notebook 内的模式清单 |

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 与文本 | 文本文件含 54 个 `===== PDF p.N =====` 标记，与论文版式（正文 10 页、参考文献、附录至 p.54）一致；PDF 为 1,029,891 字节的官方下载件，本机无 PDF 工具，未逐页渲染核对页数，也未与 proceedings 网页版做二进制比对。 |
| 论文 §3–§5、Appendix A/C/E/H/J/K/N 的关键条目 | 已与本地全文核对（见 `exact-source-anchors.md`）。 |
| 论文各表数值 | 已按本地全文逐格抄录；未与 proceedings 网页版二次比对。 |
| 官方代码 revision | `a70542e541b2104ef8fcd785778179e173fb8d70`（2025-07-23）。 |
| 标注 PDF 的内容 | 本地已用自写解码器抽取文本核对：`round_2_trim`、`round3_trim` 为 17 模式中间版，`round1_trim`、`new_benchmarks_trim` 为最终 14 模式且两者文本一致。 |
| 论文报告与代码行为的关系 | 已发现 FM-3.2/FM-3.3 命名在两处代码与论文之间互相冲突（见 `exact-source-anchors.md` 末节），未做进一步判定。 |
| LLM-judge notebook 复跑 | 尚未执行；需要 OpenAI 密钥与真实 trace，两者均未纳入来源包。 |
| IAA 一致性数值复算 | 尚未执行；标注表是 PDF 版式，未做机器可读抽取与 κ 重算。 |
| 数据与完整 benchmark 环境 | 未纳入来源包（`traces/` 13359 个文件，数据集在 Hugging Face）。 |
| 迁移到目标 Harness 的收益 | 尚未验证；论文的 case study 仅覆盖 AG2 与 ChatDev 两个 MAS。 |
