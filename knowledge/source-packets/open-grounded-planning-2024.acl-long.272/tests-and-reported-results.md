# Tests and reported results

本文件中的全部数值均为**论文报告值，不是本仓库复跑结果**。

## 论文报告结果

### 主结果（Table 3，PDF p.7）

论文的 Table 3 中，「wikiHow」三列是 19 个 wikiHow 类别的**全类别平均**（论文该组表头为 “Average of All Types”）；后 5 列是各 out-of-domain 数据集的 Pass Rate。论文只报 in-domain 的 Executability / Quality，OOD 只报 Pass Rate。

| 模型 | 方法 | wikiHow 可执行率(%) | wikiHow 质量(%) | wikiHow Pass Rate(%) | APIBank | GPT4Tools | ToolAlpaca | VirtualHome | SayCan |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vicuna-7B-v1.5-16k | Task-Retrieve | 89.60 | 27.87 | 24.97 | 36.50 | 16.30 | 19.90 | 12.40 | 14.94 |
| Vicuna-7B-v1.5-16k | Plan-Retrieve | 67.77 | 42.41 | 28.74 | 26.05 | 15.10 | 9.70 | 11.90 | 12.20 |
| Vicuna-7B-v1.5-16k | Step-wise Select | 73.17 | 12.34 | 9.03 | 20.72 | 15.80 | 10.20 | 7.10 | 1.83 |
| Vicuna-7B-v1.5-16k | DFS | 97.92 | 7.18 | 7.03 | 26.81 | 20.50 | 16.17 | 6.80 | 2.44 |
| Vicuna-7B-v1.5-16k | Retrieve and Rewrite | 80.75 | 34.88 | 28.17 | 45.44 | 22.30 | 23.63 | 16.00 | 12.50 |
| GPT-3.5 | Task-Retrieve | 95.99 | 44.43 | 42.65 | 37.26 | 23.20 | 14.93 | 26.50 | 29.27 |
| GPT-3.5 | Plan-Retrieve | 69.46 | 60.15 | 41.78 | 30.61 | 32.30 | 11.94 | 37.60 | 44.82 |
| GPT-3.5 | Step-wise Select | 93.44 | 21.21 | 19.82 | 32.32 | 23.50 | 16.67 | 30.60 | 26.83 |
| GPT-3.5 | DFS | 98.84 | 50.76 | 50.17 | 35.55 | 25.00 | 19.90 | 32.90 | 11.28 |
| GPT-3.5 | Retrieve and Rewrite | 92.98 | 58.72 | 54.60 | 43.73 | 26.60 | 28.86 | 47.00 | 41.16 |
| LLaMA-2-7B(SFT) | Task-Retrieve | 99.40 | 47.66 | 47.37 | 58.75 | 26.50 | 49.00 | 37.50 | 37.50 |
| LLaMA-2-7B(SFT) | Plan-Retrieve | 99.13 | 58.21 | 57.70 | 47.72 | 35.00 | 36.07 | 42.70 | 30.79 |
| LLaMA-2-7B(SFT) | Step-wise Select | 99.82 | 24.26 | 24.22 | 36.12 | 4.20 | 21.89 | 34.10 | 31.71 |
| LLaMA-2-7B(SFT) | DFS | 99.09 | 53.53 | 53.04 | 11.40 | 0.48 | 2.79 | 35.64 | 14.96 |
| LLaMA-2-7B(SFT) | Retrieve and Rewrite | 98.26 | 61.58 | 60.51 | 45.42 | 43.70 | 45.02 | 46.80 | 42.68 |

按论文数值整理的每个数据集 Pass Rate 最佳/次佳（论文用加粗/下划线标注）：

| 数据集 | 最佳 | 次佳 |
| --- | --- | --- |
| wikiHow（全类别平均） | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 60.51 | Plan-Retrieve, LLaMA-2-7B(SFT) — 57.70 |
| APIBank | Task-Retrieve, LLaMA-2-7B(SFT) — 58.75 | Plan-Retrieve, LLaMA-2-7B(SFT) — 47.72 |
| GPT4Tools | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 43.70 | Plan-Retrieve, LLaMA-2-7B(SFT) — 35.00 |
| ToolAlpaca | Task-Retrieve, LLaMA-2-7B(SFT) — 49.00 | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 45.02 |
| VirtualHome | Retrieve and Rewrite, GPT-3.5 — 47.00 | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 46.80 |
| SayCan | Plan-Retrieve, GPT-3.5 — 44.82 | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 42.68 |

主要可读出的结论（论文 §5.2–5.3 自述）：LLaMA-2-7B(SFT) 在 6 个数据集中的 4 个取得最佳；GPT-3.5 的 DFS 在 SayCan 上只有 11.28，而 SFT 的 DFS 在 GPT4Tools / ToolAlpaca 上塌到 0.48 / 2.79，说明 DFS 类回溯方法对模型能力高度敏感。

### OOD 详细分解（Appendix E，Table 5–9，PDF pp.13–14）

论文只在这些表里报 Pass Rate 之外的 Executability 与 Quality；下表仅摘 Pass Rate，用于与 Table 3 交叉核对。核对结果：Table 3 的 5 列 OOD 数值与 Table 5–9 的 Pass Rate 逐格一致。

| 数据集 | 模型 | Task-Retrieve | Plan-Retrieve | Step-wise Select | DFS | Retrieve and Rewrite |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| APIBank (Table 5) | Vicuna-7B-v1.5-16k | 36.50 | 26.05 | 20.72 | 26.81 | 45.44 |
| APIBank (Table 5) | GPT-3.5 | 37.26 | 30.61 | 32.32 | 35.55 | 43.73 |
| APIBank (Table 5) | LLaMA-2-7B(SFT) | 58.75 | 47.72 | 36.12 | 11.40 | 45.42 |
| GPT4Tools (Table 6) | Vicuna-7B-v1.5-16k | 16.30 | 15.10 | 15.80 | 20.50 | 22.30 |
| GPT4Tools (Table 6) | GPT-3.5 | 23.20 | 32.30 | 23.50 | 25.00 | 26.60 |
| GPT4Tools (Table 6) | LLaMA-2-7B(SFT) | 26.50 | 35.00 | 4.20 | 0.48 | 43.70 |
| ToolAlpaca (Table 7) | Vicuna-7B-v1.5-16k | 19.90 | 9.70 | 10.20 | 16.17 | 23.63 |
| ToolAlpaca (Table 7) | GPT-3.5 | 14.93 | 11.94 | 16.67 | 19.90 | 28.86 |
| ToolAlpaca (Table 7) | LLaMA-2-7B(SFT) | 49.00 | 36.07 | 21.89 | 2.79 | 45.02 |
| VirtualHome (Table 8) | Vicuna-7B-v1.5-16k | 12.40 | 11.90 | 7.10 | 6.80 | 16.00 |
| VirtualHome (Table 8) | GPT-3.5 | 26.50 | 37.60 | 30.60 | 32.90 | 47.00 |
| VirtualHome (Table 8) | LLaMA-2-7B(SFT) | 37.50 | 42.70 | 34.10 | 35.64 | 46.80 |
| SayCan (Table 9) | Vicuna-7B-v1.5-16k | 14.94 | 12.20 | 1.83 | 2.44 | 12.50 |
| SayCan (Table 9) | GPT-3.5 | 29.27 | 44.82 | 26.83 | 11.28 | 41.16 |
| SayCan (Table 9) | LLaMA-2-7B(SFT) | 37.50 | 30.79 | 31.71 | 14.96 | 42.68 |

### 消融与分析类结果

| 分析项 | 位置 | 论文报告的结论 |
| --- | --- | --- |
| 检索数量对 Task-Retrieve 的影响 | §5.5，Figure 3，PDF pp.8–9 | 只在 wikiHow-Computers and Electronics 上、且只检查输出格式；Pass Rate 随召回数先升后降，GPT-3.5 在召回 20 条时最好；召回 5 条时仍会出现不可执行步骤。 |
| 检索数量对 Plan-Retrieve / Step-wise Select 的影响 | Appendix D，Figure 4，PDF pp.12–13 | Plan-Retrieve 召回越多可执行率越低；Step-wise Select 上 Vicuna 随候选增多而上升、GPT-3.5 下降。 |
| Rewrite 的格式错误率 | §5.4，PDF p.8 | 不可执行的 Rewrite 计划中 11.84% 是格式解析错误（其余归因于幻觉）。 |
| DFS 的重复步 | §5.4，PDF p.8 | 19.32% 的 DFS 计划出现两次及以上的重复步骤。 |
| SFT 模型在 tools 上的 DFS 塌陷 | §5.3，PDF p.7 | 平均计划长度不足 1（其他方法为 1–2）；作者归因于训练数据中「拒绝」比例偏高导致模型不敢选择检索结果。 |
| 自动评判与人工评判一致性 | Appendix C，PDF p.12 | 随机抽 200 例人工评估，与 ChatGPT 自动评估的 Spearman 相关系数为 80.76%。 |
| 方法内对照案例 | Table 4，PDF p.8 | 同一任务下 Plan-Retrieve / DFS / Rewrite / golden plan 的对照，展示 DFS 的重复步与 Rewrite 的补充信息能力。 |

### 论文自述的失效与限制

| 项 | 位置 | 内容 |
| --- | --- | --- |
| 检索器未优化 | Limitation，PDF p.9 | 当前是「检索 + 生成」两阶段，作者预期任务专用检索器会更好。 |
| 动作不含参数 | Limitation，PDF p.9 | 数据集只做「把任务接地到给定动作集」，不含每个动作的参数。 |
| 评判器偏差 | Limitation，PDF p.9 | ChatGPT 评判仍带偏差与幻觉，虽有位置交换与长度惩罚，仍未被消除。 |
| 达到迭代上限 | Appendix B，PDF p.12 | 达到 20/30/20 的迭代上限意味着计划可能不完整；论文仍按可执行计，但质量受损。 |
| GPT-3.5 在 tools 上不听指令 | §5.3，PDF p.7 | 即使做了大量 prompt 工程，GPT-3.5 仍倾向生成自然语言完整步骤而非给定 API 名。 |
| 检索数量窗口窄 | §5.5，PDF pp.8–9 | 召回数过少或过多都会降低 Pass Rate，最优值只在被测试的单一设置上确定。 |

## 官方检查入口

| 检查对象 | 官方代码 |
| --- | --- |
| 生成结果是否逐任务落盘、是否有失败项 | `official-code/generate/generate_loop.py:543-551`（写 `record`）、`:594-602`（汇总 `error.json`） |
| 每个任务的执行状态与迭代轨迹 | `record["status"]` 与 `record["select_iterations"]` / `record["dfs_iterations"]` / `record["rewrite"]`（`generate_loop.py:194`、`:196-202`、`:312`、`:434`、`:445-450`） |
| 可执行率（Executability） | `official-code/evaluate/eval_utils.py:93-105` |
| 幻觉步计数 | `official-code/evaluate/eval_utils.py:245-254` |
| 质量胜率（Quality，含位置交换） | `official-code/evaluate/eval_utils.py:134-160`、`:206-242` |
| 三维度评判提示词 | `official-code/evaluate/eval_prompts.py:1-27` |
| 结果汇总（三列指标） | `official-code/evaluate/get_score_result.py:5-27` |
| 逐类别结果文件 | `official-code/evaluate/eval_utils.py:118-131` 写出的 `final_score.json` |

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过。本包内用 pypdf 重新解析，确认共 **22 页**，与 `paper-v1.txt` 的 `PDF p.1`–`PDF p.22` 标记、以及印刷页 4982–5003 一一对应。 |
| Table 3 的列结构 | 已核对。原文抽取文本丢失列对齐，本包用 PDF 文本坐标重建表头与数据行，确认结构为「方法 + 可执行率 + 质量 + 6 个 Pass Rate 列（Average of All Types / APIBank / GPT4Tools / ToolAlpaca / VirtualHome / SayCan）」，并逐格与 Appendix E 的 Table 5–9 交叉验证一致。 |
| 论文 §3.1、§3.2/Table 1–2、§3.3.1、§3.3.2、§4/Figure 2、§5.1、§5.4/Table 4、§5.5/Figure 3、Appendix B–D、Figure 4、Appendix E–F | 已与本地全文核对。 |
| 指标自洽性 | 已核对。Table 3 的 15 行 in-domain 数据均满足 Pass Rate = Executability × Quality（四舍五入误差 ≤ 0.01）。 |
| 官方代码 revision | 已固定为 `c9d3cd5e98d82498a544da81fc090b6fc72b0e4b`（2024-06-11）。本地 22 个文件与远端该 commit 的 blob 哈希逐一相同。 |
| 官方端到端生成复跑 | **尚未执行**。缺上游 `datasets/`（任务与动作库）、缺 `actions_emb.npy`，且需要 OpenAI 兼容端点与密钥。 |
| 官方评测复跑 | **尚未执行**。静态阅读发现评测侧以 `model="1106"` 调用 `get_ans`，而该快照的 `get_ans` 只接受 `vicuna` / `sft` / 含 `chatgpt` 的字符串，按原样运行会在评分阶段抛 `ValueError` 并被吞掉（详见 `exact-source-anchors.md`）。未运行验证该推断。 |
| SFT 模型的训练流程 | **未知**。论文 §5.1 说明用 FastChat、每子类 200 条、与 Alpaca 混合、3 epoch，但上游仓库不含训练脚本或训练数据。 |
| 数据集本体（`datasets/`） | 未纳入来源包（按规范剔除数据集）。 |
| 迁移到目标 Harness 的收益 | 尚未验证。 |
