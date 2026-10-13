# Tests and reported results

## 论文报告结果

Table 1（PDF p.6）给出 71 行模型 × 22 列的成绩。**以下全部为论文报告结果，不是本仓库复跑结果**；本包不含 `bfcl_eval/data/` 与其余模型适配器，无法复现这些数字。

论文表把 22 列分成：Overall Acc、Single Turn（AST 四列 + Execute 四列）、Crowd Sourced（四列）、Hallucination Measure（Irrelevance、Relevance）、Multi Turn（Base、Miss Func、Miss Param、Long Context）、Agentic（Web Search、Memory、SQL）。下列只列已核对过列位置的字段（核对依据见本节末）：

| 模型（论文写法） | Overall Acc | Hallucination: Irrelevance | Multi Turn: Base | Multi Turn: Long Context | Agentic: Web Search | Agentic: Memory | Agentic: SQL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt-4o-2024-11-20 (Prompt) | 66.4 | 83.8 | 59.0 | 55.0 | 64.0 | 6.0 | 78.0 |
| gpt-4o-2024-11-20 (FC) | 65.8 | 83.1 | 62.5 | 58.0 | 82.0 | 0.0 | 81.0 |
| GPT-4-turbo-2024-04-09 (FC) | 60.9 | 83.8 | 54.0 | 49.5 | 66.0 | 4.0 | 50.0 |
| GPT-4o-mini-2024-07-18 (FC) | 60.6 | 74.7 | 47.5 | 40.5 | 78.0 | 6.0 | 66.0 |
| o1-2024-12-17 (Prompt) | 59.1 | 87.8 | 50.5 | 44.5 | 5.0 | 12.0 | 91.0 |
| Qwen2.5-72B-Instruct (Prompt) | 57.0 | 72.8 | 24.5 | 12.0 | 54.0 | 8.0 | 70.0 |
| Claude-3.5-Sonnet-20241022 (FC) | 53.8 | 74.0 | 55.0 | 47.5 | 74.0 | 4.0 | 60.0 |
| o1-2024-12-17 (FC) | 52.8 | 82.0 | 52.5 | 43.0 | 48.0 | 12.0 | 83.0 |
| Claude-3.5-Sonnet-20241022 (Prompt) | 49.4 | 64.4 | 9.0 | 10.5 | 68.0 | 0.0 | 60.0 |
| Gemma-3-1b-it (Prompt)，表末 | 12.5 | 30.9 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |

对全部 71 行做列统计（同样只是对论文表格的重新计数，不是复跑）：

| 观察 | 数值 |
| --- | --- |
| Overall Acc 范围 | 12.5（Gemma-3-1b-it Prompt）至 66.4（gpt-4o-2024-11-20 Prompt） |
| Agentic: Memory | 最高 12.0（o1-2024-12-17 的 Prompt 与 FC 两行并列），71 行中有 57 行为 0.0 |
| Agentic: Web Search | 最高 83.0（claude-3.5-haiku-20241022 FC），18 行为 0.0 |
| Agentic: SQL | 最高 91.0（o1-2024-12-17 Prompt），8 行为 0.0 |
| Multi Turn 四列最高值 | Base 62.5、Miss Func 41.0、Miss Param 48.5、Long Context 58.0，均远低于单轮同量级列（AST/Execute 单轮多在 90 上下） |
| 并行列出现 0.0 的行数 | Single Turn AST Parallel 2 行、AST Parallel Multiple 3 行、Execute Parallel 2 行、Execute Parallel Multiple 6 行、Crowd Sourced Parallel 4 行、Crowd Sourced Parallel Multiple 5 行 |

论文正文还报告了这些量化结论（位置见 `exact-source-anchors.md`）：

| 结论 | 数值 |
| --- | --- |
| prompting 模型解码问题更多（§5.1，PDF p.5） | 平均 412.93 条 vs FC 模型 182.5 条，共 4 251 条条目 |
| multiple 类目函数调用个数错误（§5.1，PDF p.6） | 仅算成功解码的回复，FC 模型平均 77.5 次 vs prompting 模型 21 次 |
| 旗舰 FC 模型并行能力回退（§5.3，PDF p.7） | o1-2024-12-17-FC 与 claude-3-5-sonnet-20241022-FC；与 Table 1 中两者并行列接近 0 一致 |
| 记忆类目最好成绩（§5.6，PDF p.9） | 12%（openai o1-2024-12-17 (FC)）；与 Table 1 统计出的 Memory 列最高值一致 |
| 污染迹象（§5.5，PDF p.8–9，Tables 2–3） | Salesforce xLAM-7B 在 crowd-sourced 集上 PPL 从 3.67 升到 5.09（char-NLL 同步上升），与多数模型的下降方向相反 |
| 多轮确定性错误分析规模（§5.4.1，PDF p.7，Figure 4） | 800 条多轮条目 |
| AST 与 Exec 打分一致性（§4.3，PDF p.5，Figure 3） | 原文只称"强相关"，未给相关系数 |

引用 Table 1 时的两个注意点：

1. 表头在文本提取中被压成三行，列位置靠表头顺序对齐。本包核对了三处可独立验证的位置：Overall Acc 为第一列；最后三列为 Web Search / Memory / SQL（用 §5.6 的"12%"与 Memory 列最高值 12.0 互证）；`parallel` 相关列的位置与 §5.3 所述 o1-2024-12-17-FC、claude-3-5-sonnet-20241022-FC 并行能力回退互证（两行在这些列上分别为 0.0 与 3.5/5.0/4.0/0.0）。其余列未逐列反查，引用前应回到 PDF p.6。
2. 表中 `Amazon-Nova-Lite-v1:0 (FC)` 出现两行，分类列数值完全相同，仅 Overall Acc 与 Agentic 三列不同（52.1 与 43.7；Web Search 62.0 与 10.0，SQL 58.0 与 9.0），论文未说明差异来源；引用该模型的数字时必须指明是哪一行。

## 官方检查入口

BFCL 目录内没有单元测试目录、`pytest.ini`/`tox.ini`，`pyproject.toml` 也没有 pytest 配置；官方"检查"以可执行脚本与 CLI 自检命令为主，CI 相关配置在上游 `.github/`（未纳入本包）。

| 检查对象 | 官方代码 | 说明 |
| --- | --- | --- |
| 测试类别与类别组是否齐全 | `official-code/TEST_CATEGORIES.md`；`bfcl test-categories`（`bfcl_eval/__main__.py:67-81`） | 打印 `TEST_COLLECTION_MAPPING` 中的类别与组。 |
| 模型名是否可用 | `bfcl models`（`bfcl_eval/__main__.py:83-94`）、`official-code/bfcl_eval/constants/supported_models.py` | 列出 `MODEL_CONFIG_MAPPING` 的键。 |
| 版本记录 | `bfcl version`（`bfcl_eval/__main__.py:60-65`） | 官方提示"PyPI 版本仍在演进，可复现性以 commit 为准"。 |
| 函数文档格式 | `official-code/bfcl_eval/scripts/check_func_doc_format.py` | 校验 function doc 必须恰有三个顶层字段、参数类型落在枚举内等，并打印出问题的条目 ID。 |
| 非法 Python 参数名 | `official-code/bfcl_eval/scripts/check_illegal_python_param_name.py` | 用 `keyword.kwlist` 检查参数名与 Python 关键字冲突，并回写修正。 |
| 多轮函数文档一致性 | `official-code/bfcl_eval/scripts/compile_multi_turn_func_doc.py`、`_compile_helper.py` | 从后端类方法签名重新生成 `multi_turn_func_doc/*.json`，可与现有文档比对。 |
| 多轮真值对话可复现 | `official-code/bfcl_eval/scripts/visualize_multi_turn_ground_truth_conversation.py` | 用 `execute_multi_turn_func_call` 重跑真值调用并输出每轮状态，是核对多轮真值的主要手段。 |
| 端到端评测 | `bfcl generate` → `bfcl evaluate` → `bfcl scores` | 需要 `bfcl_eval/data/**` 数据集与模型 API key。 |

上表脚本都以 `bfcl_eval/data/` 为输入（`PROMPT_PATH`、`POSSIBLE_ANSWER_PATH`、`MULTI_TURN_FUNC_DOC_PATH`），本包未纳入数据，因此这些脚本在本包内不能直接运行。

## 当前核验状态

| 项目 | 状态与依据 |
| --- | --- |
| PDF 可解析 | 已通过：`paper/paper-v1.pdf` 1 200 643 字节，`/Type /Page` 计数 22，与 22 个 `===== PDF p.N =====` 标记一致。 |
| 论文页码与锚点 | 已通过：`exact-source-anchors.md` 中每一处章节/图表页码均回到 `paper/paper-v1.txt` 的 p.N 标记核对。 |
| 论文 Table 1 | 已部分核对：上表与统计中引用的数值逐字取自 txt；列位置用三处可独立验证的位置交叉验证（见上），其余列未逐列反查。 |
| 官方代码 revision | `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`（2026-03-23，branch `main`）。 |
| official-code 体积 | 已通过：69 个文件、979 896 字节（约 0.93 MiB），无单文件 >1 MB；最大文件 `long_context.py` 190 330 字节。 |
| Python 语法可解析 | 已通过：59 个 `.py` 全部 `ast.parse` 通过（本地以 `python3 -I` 运行解析脚本，未执行快照代码）。 |
| 数据集与模型输出 | 未纳入来源包（`bfcl_eval/data/**` 与 `result/`）；无 `possible_answer` 真值。 |
| 官方端到端复跑（generate + evaluate） | 尚未执行：缺数据集与 API key。 |
| 检查器的样例级本地运行 | 尚未执行：未构造样例调用 `ast_checker`、`multi_turn_checker`、`agentic_checker`；接口签名已在 `configs-and-examples.md` 中按代码核对。 |
| 论文报告数字与本地代码行为的一致性 | 仅做了三处互证（Memory 12.0、并行列回退、权重表）。代码与论文存在若干实现差异（agentic 为包含式匹配而非严格相等、executable/rest/sql/chatable 类别被跳过、多轮无关检查器与方法顺序检查器未生效），已记录在 `exact-source-anchors.md`，未作为"论文结论错误"处理。 |
| 迁移到目标 Harness 的收益 | 尚未验证。 |
