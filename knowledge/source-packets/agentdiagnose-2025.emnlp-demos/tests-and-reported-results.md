# Tests and reported results

## 论文报告结果

以下数值均为**论文结果，非本仓库复跑结果**。

### Table 1：人评与自动评分的相关性（PDF p.6）

30 条人工标注轨迹；标注者与模型拿到同样的 reasoning-action 序列与评分细则。

| 维度 | Pearson r | Spearman ρ | Kendall τ |
| --- | ---: | ---: | ---: |
| backtrack & explore | 0.39 | 0.43 | 0.36 |
| task decomposition | 0.78 | 0.86 | 0.76 |
| observation reading | 0.62 | 0.63 | 0.60 |
| self-verification | 0.56 | 0.58 | 0.55 |
| objective quality | 0.54 | 0.61 | 0.56 |
| **Overall** | **0.57** | **0.62** | **0.56** |

论文对该表的解释：task decomposition 一致性最高（0.78），说明该行为较易识别；backtracking & exploration 最低（0.39），论文归因于抽取回溯行为并判断其精度与正确性本身困难（§5.1，PDF p.6）。

### Figure 6：用评估分数筛选训练数据后的 WebArena 成功率（PDF p.6）

设定：NNetNav-Live 46k 训练样本，用 Gemini 2.5 Pro 作 LLM judge 打分，取 top 6k；按 NNetNav 的设置微调 Llama-3.1-8B，并在 WebArena 上用 BrowserGym 评测。

| 训练集 | 样本数 | WebArena 成功率 |
| --- | ---: | ---: |
| llama3.1-8B-46k（全集） | 46k | 7.8% |
| llama3.1-8B-top-6k（筛选后） | 6k | 8.7% |

需要注意论文内部的一处不一致：§5.2 与摘要都记为“提高 **0.98**”，而 Figure 6 柱标为 7.8% → 8.7%（相差 0.9 个百分点）。本来源包按原文并列记录，不作修正。数据量为原来的 13%。

### 其他可核对的量化表述

| 内容 | 位置 | 数值 |
| --- | --- | --- |
| NNetNav-Live 训练样本总数 | §5.2，PDF p.6 | 46k |
| 筛选用作微调的样本数 | §5.2，PDF p.6 | 6k（13%） |
| 人工标注轨迹数 | §5.1，PDF p.6；§8，PDF p.7 | 30 |
| 内置评估维度数 | 摘要、§3，PDF pp.1–4 | 5 |
| 内置动作词抽取选项数 | §3，PDF p.4 | 6 |

## 官方检查入口

**官方仓库没有任何测试**：`6ac7bedd` 快照的 44 个文件中不存在 `tests/`、`*_test.py`、`test_*.py`、`conftest.py`、`pytest.ini`、`tox.ini` 或 CI 测试工作流。因此没有可执行的官方测试套件，只能借助下列代码内建的检查点。

| 检查对象 | 官方代码 | 说明 |
| --- | --- | --- |
| 评分提示与 token 消耗（不发 API） | `official-code/evaluate_trajectories.py:339`、`:131-132`；`official-code/evaluator/scorers/base.py:90-100` | `--dry-run` 调用 `LLMScorer.dry_run`，用 tiktoken `cl100k_base` 数 token，返回 `details.prompt` 供人工核对提示拼装。这是唯一不依赖外部服务即可跑通的检查。 |
| LLM 响应能否被解析 | `official-code/evaluator/scorers/reasoning_quality.py:139-146`；`objective_quality.py:82-89`、`:137-146` | 解析失败时返回 `score=0.0` 且 `details.error` + `details.raw_response`；`confidence` 为 0.0。成功时 `confidence` 分别为 0.9。 |
| 目标质量评分的重试行为 | `official-code/evaluator/scorers/objective_quality.py:93-136` | 最多 2 次重试；仍失败则 `details.error` = `Failed after N attempts`。 |
| 断点续跑是否生效 | `official-code/evaluate_trajectories.py:100-119` | 已有 `--output-json` 中出现的轨迹会被跳过，并在结尾打印累计 token 用量。 |
| 中间落盘是否正常 | `official-code/evaluate_trajectories.py:134-161` | 每 50 条写一次，先写 `.temp` 再 rename，失败只打印 warning 不中断。 |
| 轨迹能否被解析 | `official-code/evaluator/trajectory.py:179-206` | `from_json` 对缺失字段一律取默认值（`""`、`-1`、`0`、`[]`），不会因字段缺失报错；解析失败只会在 `load_trajectory` 处打印并跳过该文件（`evaluate_trajectories.py:25-33`）。这是宽松解析，不构成校验。 |
| Dashboard 数据是否装载成功 | `official-code/dashboard/backend/main.py:1399-1417` | 从 `DASHBOARD_DATA_FILE` 读 pickle，打印装载的结果数与轨迹数。 |

`navigation_path` 评分器需要特别说明：它的 `score` 恒为 `0.0`、`confidence=0.8`（`navigation_path_scorer.py:42-58`），只在 `details` 里给出导航统计。把它算进 overall 会拉低加权平均，看结果时应单独处理。

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，9 页（demo 论文）。 |
| 论文 §3–§5、Table 1、Figure 3–6、附录 A 评分细则 | 已与本地全文逐条核对。 |
| 官方代码版本 | 已固定为 `6ac7bedd`（2025-07-03）；本地快照 44/44 文件与上游该 commit 的 blob 哈希逐一比对一致。 |
| 论文 Listing 1 与代码 CLI 参数的一致性 | 已核对：`--input` / `--scorers` / `--output-json` 三个参数与论文一致。 |
| 五个维度的评分细则 | 论文附录 A（PDF p.9）与 `scorers/prompts/prompt.py` 的 system prompt 已比对，分档文字一致。 |
| 示例轨迹数据 | 未纳入（12MB，9 个文件全部 >100KB）。 |
| 官方端到端复跑（评估 46k 样本或微调 Llama-3.1-8B） | 尚未执行；论文未提供完整的微调与评测脚本。 |
| 评估器最小运行（含 `--dry-run`） | 尚未执行；仓库无 Python 依赖清单，需先自行安装 litellm/spacy/benepar/tiktoken 等。 |
| 真实 API 评分调用 | 尚未执行（需要 `LLM_API_KEY` 与计费额度）。 |
| 前端 dashboard 构建（`npm run build`） | 无法执行：`+page.svelte:4-10` import 的 7 个 `lib/components/*.svelte` 不在上游快照中。 |
| 导航图/t-SNE/词云的可视化效果 | 未知；需要先补齐前端组件并生成对应的产物目录。 |
| 迁移到目标 Harness 的收益 | 尚未验证。 |

## 论文自述的失效条件

来自 §7 Limitations（PDF p.6），属于**论文自述**而非本仓库实测：

- 主要面向 web navigation 任务设计，对 coding 等其他场景的适用性未验证。
- 多模态场景未覆盖。
- 评估系统整体依赖 LLM-based evaluation，论文建议后续用带细粒度人工标注的专用评估器替换以提升可靠性。

结合 Table 1 可确认的失效边界：backtracking & exploration 维度的人机一致性只有 0.39，在论文自己的 30 条样本上即属于弱相关，单独用该维度做筛选决策缺少证据支持。
