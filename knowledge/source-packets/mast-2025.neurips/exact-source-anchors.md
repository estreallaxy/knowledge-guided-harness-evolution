# Exact source anchors

页码一律以 `paper/paper-v1.txt` 的 `===== PDF p.N =====` 标记为准（共 54 页）。代码行号以 `source-packet.json` 固定的 revision `a70542e` 为准。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 研究问题与四项贡献（MAST-Data、MAST、LLM annotator、案例研究） | §1，PDF pp.1–3 | 论文把 MAS 表现增益有限归因于系统设计而非仅模型能力；不能推出「多 Agent 一定优于单 Agent」或反向结论。 |
| 7 个开源 MAS 的失败率区间 41%–86.7% | §1，PDF p.2；Figure 5，PDF p.26 | 正文写 7 个 MAS，Figure 5 实际只画了 6 个（Magentic-One/GAIA、AG2/OlympiadBench、AppWorld/Test-C、HyperAgent/SWE-Bench Lite、ChatDev/ProgramDev、MetaGPT/ProgramDev，失败率依次 62.0%、41.0%、86.7%、74.7%、66.7%、60.0%）；OpenManus 的失败率未出现在 Figure 5。论文注明各系统 benchmark 不同、数值不可直接互比，不能当作跨系统性能排名。 |
| MAST-Data 配置与规模（1642 条 trace，7 框架，4 模型族） | §1，PDF pp.2–3；Table 1，PDF p.3 | Table 1 给出每条来源的 MAS、benchmark、模型与标注类型（HE/HA/LA）及 trace 数（30/100/206/193/168/165 等）；不能推出这些 trace 覆盖了各 MAS 的全部任务分布。 |
| 14 个失败模式 / 3 个类别 / 3 个执行阶段 | §4，PDF pp.7–8；Figure 1，PDF p.2 | Figure 1 把模式映射到 Pre-Execution、Execution、Post-Execution 阶段，并给出在 1642 条 trace 上的占比；「跨阶段」表示该问题可在多个阶段显现，不是独立的第三个维度。 |
| Grounded Theory 建立分类法的过程 | §3.1，PDF p.5 | 150 条 trace、五个框架（HyperAgent、AppWorld、AG2、ChatDev、MetaGPT）、六个专家、每人 20 小时以上标注、迭代至理论饱和；不能推出该过程使用了预定义假设。 |
| 分类法定义的多轮一致性校验（IAA，κ = 0.88） | §3.2，PDF pp.5–6；Figure 2，PDF p.5 | 每轮 3 名专家独立标注 5 条随机 trace，共 3 轮，讨论消解分歧约 10 小时，最终平均 Cohen's κ = 0.88；这 88% 只覆盖 IAA 子集，不等于全量 1642 条的质量。 |
| LLM-as-a-Judge 流水线与人类标注的一致性 | §3.3，PDF p.6；Table 2，PDF p.6 | prompt 含 trace + MAST 定义 + few-shot 示例，模型为 OpenAI o1；报告 accuracy 0.94、Cohen's κ 0.77（few-shot），无 few-shot 时 0.89/0.58；不能推出该流水线在其他 MAS 或模型上保持同样一致性。 |
| 分类法与标注器的跨系统/跨任务泛化验证 | §3.4，PDF p.6 | 在 OpenManus、Magentic-One 与 MMLU、GAIA 上多做一轮标注得到 κ = 0.79，且未修改分类法；这是单一额外轮次的结果，不能推出对任意新 MAS 都成立。 |
| FC1 System Design Issues 的定义与 5 个模式 | §4 FC1，PDF p.7；Appendix A.1，PDF p.24 | FM-1.1 11.8%、FM-1.2 1.5%、FM-1.3 15.7%、FM-1.4 2.80%、FM-1.5 12.4%（占 1642 条）；论文把 disobey specification 同时归因于 MAS 设计、用户 prompt 与底层模型三点，不能只归因于模型指令遵循。 |
| FC2 Inter-Agent Misalignment 的定义与 6 个模式 | §4 FC2，PDF pp.7–8；Appendix A.2，PDF pp.24–25 | FM-2.1 2.20%、FM-2.2 6.80%、FM-2.3 7.40%、FM-2.4 0.85%、FM-2.5 1.90%、FM-2.6 13.2%；论文认为标准化通信协议（MCP、A2A）不足以解决 FC2，需要「社会推理」能力；这是论文的论证，不是实验对照结论。 |
| FC3 Task Verification 的定义与 3 个模式 | §4 FC3，PDF p.8；Appendix A.3，PDF p.25 | FM-3.1 6.20%、FM-3.2 8.20%、FM-3.3 9.10%；论文主张「有 verifier」不等于可靠，且需要多层次验证。 |
| 分类法各类别的占比 | Figure 1 标题，PDF p.2 | System Design Issues 44.2%、Inter-Agent Misalignment 32.3%、Task Verification 23.5%（1642 条 trace，与 §4 中各 FM 占比之和一致）；Figure 1 中标 FM-2.4 为 0.80%，§4 正文写 0.85%，两处存在 0.05 个百分点的不一致。 |
| 类别之间的区分度（相关性分析） | Appendix E，PDF p.29；Figure 6、Figure 7 | 三个类别之间的相关性为 0.17–0.32，模式之间最高 0.63；论文据此认为分类法内部区分度成立，同时承认高相关模式会让自动标注器混淆根因。 |
| 各 MAS 的失败画像（210 条 trace） | §5.1，PDF p.9；Figure 4，PDF p.8 | Figure 4 只统计每个系统前 30 条 trace；类别占比 41.8%/36.9%/21.3%，与 Figure 1 的全量占比不同，不能混用。 |
| 模型与架构对失败分布的影响 | §5.1，PDF p.9；Appendix F，PDF pp.30–31；Figure 8、Figure 9 | MetaGPT 中 GPT-4o 比 Claude 3.7 Sonnet 少 39% 的 FC1 失败；ProgramDev 上 MetaGPT 比 ChatDev 少 60–68% 的 FC1/FC2 失败但多 1.56 倍 FC3；不能推出模型或架构在所有任务上同向。 |
| 失败模式与任务成败的关系 | Appendix J.1，PDF p.36；Table 7 | FM-1.5、FM-2.4 几乎只出现在失败运行中，而 FM-3.2、FM-3.3 在成功运行中也频繁出现；样本为 ChatDev/MetaGPT 的各 20/18 条，比例不可外推。 |
| 不同 benchmark 的失败率 | Appendix J.2，PDF p.37；Table 8 | 固定 AG2 + GPT-4o，GSM / MMLU / Olympiad 的 FC1、FC2、FC3 每 trace 失败率；benchmark 越难失败率越高，不能据此比较不同 MAS。 |
| 开源模型的失败模式分布 | Appendix I，PDF pp.35–36；Table 6 | 400 条 trace，Qwen2.5-Coder-32B-Instruct 与 CodeLlama-7b-Instruct-hf 各在 ChatDev、MetaGPT 上的逐模式计数；论文结论是开源模型失败频率高于 GPT-4o/Claude-3。 |
| 干预案例研究（AG2 与 ChatDev） | Appendix H，PDF pp.33–35；Table 5，PDF p.34 | AG2/GSM-Plus 三种配置 × GPT-4/GPT-4o 各 6 次重复；ChatDev 在 ProgramDev-v0 与 HumanEval 上 baseline 25.0/89.6 → 改 prompt 34.4/90.3 → 改拓扑 40.6/91.5。Wilcoxon 检验 p 值 0.4（GPT-4）与 0.03（GPT-4o）说明改进并非在所有模型上显著。 |
| 干预前后的失败模式分布变化 | Appendix H.3，PDF pp.34–35；Figure 10、Figure 11 | 用同一 LLM-as-a-Judge 重新标注干预前后的 trace，观测到各模式下降，拓扑改动比 prompt 改动更有效；这是论文自身的观察，未经外部复现。 |
| 战术手段与结构性策略的对应关系 | Appendix G，PDF pp.32–33；Table 4，PDF p.33 | Table 4 给出「失败类别 → 战术手段 / 结构性策略」的映射建议，属论文提出的方向性主张，不是已验证的方法清单。 |
| 标注成本 | Appendix K，PDF p.37；Table 9 | 全部 trace 的平均 API 成本 1.8 美元，按框架 0.3740–4.1409 美元；成本随 trace 长度变化，与具体模型价格绑定，不能作为当前价格下的预算依据。 |
| `agentdash` Python 库用法 | Appendix C，PDF p.28 | 论文给出 `pip install agentdash` 与 `annotator(...).produce_taxonomy(trace)` 的调用示例；本来源包内的代码快照没有该包，不能据此确认其可安装性或接口现状。 |
| ProgramDev / ProgramDev-v2 任务来源 | Appendix D，PDF p.28 | ProgramDev 30 题、ProgramDev-v2 100 题；论文把任务文件指向仓库 `traces/programdev/programdev_dataset.json`，该文件属于未纳入本来源包的 `traces/` 数据集。 |
| 每个失败模式的原文示例 | Appendix N，PDF pp.45–54 | N.1–N.13 逐条给出 MAS、任务、发生了什么与原文片段（如 N.1 HyperAgent 的 step repetition + conversation reset + disobey role specification 组合）。这些是人工挑选的例证，不是随机抽样。 |
| 干预所用 prompt 全文 | Appendix L，PDF pp.38–41；Appendix M，PDF pp.42–44 | AG2 的初始/结构化 prompt 与 Problem Solver、Coder、Verifier 三个角色 prompt；ChatDev 的原始与修改后角色 prompt（Programmer、Test Engineer、Code Reviewer、CEO、CTO）。 |
| 闭源系统无法纳入细粒度标注 | Appendix B.3，PDF p.27 | Manus 等闭源平台不公开底层模型与完整执行 trace，只能做任务正确性的人工评测（Manus 在 ProgramDev 上 60%），无法进入 MAST-Data 的失败模式标注；不能推出闭源系统失败率更低。 |

## 官方代码

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| 14 个失败模式的定义文本 | `official-code/taxonomy_definitions_examples/definitions.txt:1-133` | 逐模式的正式定义、成因与后果，是 LLM judge 的 prompt 输入，也是人工标注的参照。各模式起始行：1.1→1、1.2→4、1.3→7、1.4→24、1.5→27、2.1→69、2.2→72、2.3→75、2.4→78、2.5→81、2.6→84、3.1→102、3.2→104、3.3→115。 |
| 各失败模式的带原文示例 | `official-code/taxonomy_definitions_examples/examples.txt:1-1116` | 以 `### 模式名 ###` 分隔的示例集（标题位于第 5、174、419、472、578、617、641、744、761、781、828、857、870、883、903、914、932、948、961、977、990、1052、1068 行），作为 few-shot 材料。 |
| 判定 prompt 的完整结构 | `official-code/llm_judge_pipeline.ipynb:38-94` | 要求模型输出 A 摘要、B 任务是否完成、C 十四个失败模式的 yes/no，并规定 `@@` 包裹的回答边界。 |
| 模型与调用配置 | `official-code/llm_judge_pipeline.ipynb:9-29` | 客户端初始化（`:13-19`）、`model='o1'`（`:27`）、`temperature=1.0`（`:29`）；文件顶部同时留有 `NousResearch/Meta-Llama-3-8B-Instruct` 与本地 `base_url="http://localhost:8000/v1"` 的痕迹，实际调用为 OpenAI o1。 |
| 定义与示例的注入方式 | `official-code/llm_judge_pipeline.ipynb:36, 90, 92, 103` | 第 36 行读 `definitions.txt`，第 103 行读 `examples.txt`，再分别拼到 prompt 尾部的 `{definitions}`（`:90`）与 `{examples}`（`:92`）位置。 |
| 批量评测循环与容错 | `official-code/llm_judge_pipeline.ipynb:144-182` | 逐条调用、单条按 1,048,570 字符截断（第 158-159 行）、每轮写 `saved_results/o1_results_checkpoint.pkl` 且每 10 条备份一次。 |
| 答案解析成 14 维二元标注 | `official-code/llm_judge_pipeline.ipynb:198-280` | `parse_responses` 用多套正则从自由文本中抽取每个模式的 yes/no（字典初始化在第 211-216 行），全部失败时默认 0；解析鲁棒性依赖模型遵守格式。 |
| 按来源分组统计失败率 | `official-code/llm_judge_pipeline.ipynb:284-299, 301-350` | 先打印各模式的 yes 占比，再用 `source_sizes = [30,30,30]` 的滑动分组算每来源均值；分组是硬编码的，换数据集必须同步改。 |
| 人工标注一致性原始材料 | `official-code/inter_annotator_agreement_annotations/interannotator_annotations_round_2_trim.pdf`、`interannotator_annotations_round3_trim.pdf` | 17 模式中间版本（FC1 1.1–1.7、FC2 2.1–2.7、FC3 3.1–3.3）的按系统 × 标注者 TRUE/FALSE 矩阵，带分歧讨论备注；标注集合为 AppWorld、HyperAgent、AG2、ChatDev、MetaGPT 的 Traces Set 2 / Set 3。 |
| 新 benchmark 的一致性轮次 | `official-code/inter_annotator_agreement_annotations/interannotator_annotations_new_benchmarks_trim.pdf`、`interannotator_annotations_round1_trim.pdf` | 用最终 14 模式分类法对 MMLU-ChatDev、MMLU-MetaGPT、GAIA-Magentic、GAIA-OpenManus 的标注矩阵，对应论文 §3.4 的 κ = 0.79 泛化验证；两个文件抽取出的文本内容一致，仅二进制编码不同。 |
| 仓库入口与数据集下载 | `official-code/README.md:1-53` | 指向 Hugging Face 数据集与 arXiv/博客，并给出两条 `hf_hub_download` 片段。 |

## 代码与论文不一致之处（使用前必须知道）

| 项目 | 论文 | 代码快照 |
| --- | --- | --- |
| FM-3.2 / FM-3.3 的命名 | 3.2 No or incomplete verification（8.20%）、3.3 Incorrect verification（9.10%），见 §4 FC3 与 Appendix A.3 | `definitions.txt:104` 把 3.2 写作 Weak Verification、`:115` 把 3.3 写作 No or Incorrect Verification；`llm_judge_pipeline.ipynb:64-65` 反过来写成 3.2 No or Incorrect Verification、3.3 Weak Verification。三者两两不一致。 |
| 分类法版本 | 最终 14 模式 | `round_2_trim.pdf`、`round3_trim.pdf` 记录的是 17 模式的中间版本；`definitions.txt`、`examples.txt` 与最终版一致。 |
| FM-2.6 的称呼 | Reasoning-Action Mismatch（§4、Figure 1） | `definitions.txt:84` 与 notebook 均写作 Action-Reasoning Mismatch；`round3_trim.pdf` 中为 Inconsistency between reasoning and action。 |
| 可调用的库接口 | Appendix C 描述 `pip install agentdash` | 快照内没有 `agentdash` 包，只有 notebook 形式的流水线。 |
