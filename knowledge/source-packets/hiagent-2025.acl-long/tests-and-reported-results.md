# Tests and reported results

以下所有数值均为**论文报告结果，不是本仓库复跑结果**。页码以 `paper/paper-v1.txt` 的 `===== PDF p.N =====` 标记为准。

## 论文报告结果

### 主结果（Table 1，PDF p.5）

五任务，GPT-4（gpt-4-turbo）同时作 policy 与 summarizer，每任务 1 个 in-context example，论文报告的最大步数 30。`Context` 与 `Time` 是相对 STANDARD（=100%）的比值，括号内为相对变化。

| 任务 | 方法 | SR↑ | PR↑ | Steps↓ | Context↓ | Time↓ |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blocksworld | STANDARD | 30.00 | 35.00 | 25.00 | 100% | 100% |
| Blocksworld | HIAGENT | 60.00 (+30.00) | 80.00 (+45.00) | 18.60 (-6.40) | 67.46% (-32.54%) | 63.47% (-36.53%) |
| Gripper | STANDARD | 50.00 | 87.75 | 25.20 | 100% | 100% |
| Gripper | HIAGENT | 50.00 (+0.00) | 86.25 (-1.50) | 24.80 (-0.40) | 49.99% (-50.01%) | 70.46% (-29.54%) |
| Tyreworld | STANDARD | 10.00 | 39.28 | 28.40 | 100% | 100% |
| Tyreworld | HIAGENT | 60.00 (+50.00) | 75.83 (+36.55) | 19.00 (-9.40) | 73.58% (-26.42%) | 77.58% (-22.42%) |
| Barman | STANDARD | 10.00 | 17.50 | 26.85 | 100% | 100% |
| Barman | HIAGENT | 30.00 (+20.00) | 40.83 (+23.33) | 24.50 (-2.35) | 67.02% (-32.98%) | 95.54% (-4.46%) |
| Jericho | STANDARD | 5.00 | 13.51 | 26.60 | 100% | 100% |
| Jericho | HIAGENT | 10.00 (+5.00) | 29.85 (+16.34) | 26.15 (-0.45) | 66.86% (-33.14%) | 95.85% (-4.15%) |
| Overall | STANDARD | 21.00 | 38.61 | 26.41 | 100% | 100% |
| Overall | HIAGENT | 42.00 (+21.00) | 62.55 (+23.94) | 22.61 (-3.80) | 64.98% (-35.02%) | 80.58% (-19.42%) |

读法：成功率总体翻倍（21 → 42），但 Gripper 上 SR 持平、PR 反而 -1.50；Barman 与 Jericho 的时间只降 4% 左右。因此"平均收益"不等于"每个任务都收益"。

### 消融（Table 2，PDF p.7；分析在 §5.1，PDF pp.5–6）

环境为 Tyreworld。"w/o OS" 去掉 Observation Summarization（改用轨迹中最后一条 observation 作为摘要），"w/o TR" 去掉 Trajectory Retrieval，"w/o OS & TR" 两者都去掉。

| 设置 | SR↑ | PR↑ | Steps↓ | Context↓ | Time↓ |
| --- | ---: | ---: | ---: | ---: | ---: |
| HIAGENT | 60.0 | 75.8 | 19.0 | 100.0% | 100.0% |
| w/o OS | 30.0 (-30.0) | 68.2 (-7.6) | 24.2 (+5.2) | 110.8% (+10.8%) | 122.5% (+22.5%) |
| w/o TR | 50.0 (-10.0) | 76.9 (+1.1) | 21.2 (+2.2) | 105.0% (+5.0%) | 107.5% (+7.5%) |
| w/o OS & TR | 30.0 (-30.0) | 62.4 (-13.4) | 26.2 (+7.2) | 107.2% (+7.2%) | 121.2% (+21.2%) |

两个模块都必要，且摘要的贡献大于检索（OFF 掉摘要时 SR -30，步数与上下文都上升）。注意 §5.1 正文写 w/o TR 的 steps "increased by 1.2"、w/o OS & TR 的 SR "decreasing by 20%"，与表格的 `+2.2` 和 `-30.0` 不一致。

### 不是仅靠任务分解（Table 3，PDF p.8；分析在 §5.3，PDF p.6）

环境为 Tyreworld。"w. TD" = 只让 LLM 先产出 subgoal，但不遮蔽历史轨迹。

| 方法 | SR↑ | PR↑ | Steps↓ | Context↓ | Time↓ |
| --- | ---: | ---: | ---: | ---: | ---: |
| STANDARD | 10.0 | 39.3 | 28.4 | 100% | 100% |
| w. TD | 40.0 (+30.0) | 67.4 (+28.1) | 22.8 (-5.6) | 112.8% (+12.8%) | 105.7% (+5.7%) |
| w. HIAGENT | 60.0 (+50.0) | 75.8 (+36.5) | 19.0 (-9.4) | 73.6% (-26.4%) | 77.6% (-22.4%) |

结论是分解本身有收益（+30 SR），但比 HiAgent 低 20 个点，且上下文反而变长（112.8%）。

### 与 Tree-Planner 对比（Table 4，PDF p.20；Appendix C.2）

环境为 Tyreworld，只比较 SR 与 Context Efficiency。

| 方法 | SR↑ | Context↑ |
| --- | ---: | ---: |
| HIAGENT | 60.0% | 100.0% |
| Tree-Planner | 40.0% | 94.7% |

### 统计与图（论文报告）

| 项目 | 位置 | 数值 |
| --- | --- | --- |
| Progress Rate 的 Wilcoxon signed-rank 检验 | §5.5，PDF p.7 | 统计量 144.0，p = 2.38e-5 |
| Average Steps 的 Wilcoxon signed-rank 检验 | §5.5，PDF p.7 | 统计量 112.5，p = 0.0016 |
| 各步数下的 progress rate | §5.2 / Figure 3，PDF pp.6–7 | HiAgent 每档都高于 STANDARD 且随步数继续增长；只以图像给出，无原始数据 |
| 各步数下的可执行动作比例 | §5.4 / Figure 4，PDF p.6–7 | HiAgent 长步数下保持 >80%；STANDARD 在 blocksworld 步数 >20 时降到 <10% |

## 官方检查入口

上游仓库**没有测试套件**、没有 `conftest.py` / `pytest.ini` / CI 配置；`requirements.txt` 里的 `pytest` 是 AgentBoard 的遗留依赖。可用的"检查"只有运行结果文件：

| 检查对象 | 官方入口 | 本包是否纳入 |
| --- | --- | --- |
| 单次运行的成功率 / 进度率 / grounding 汇总 | `agentboard/eval_main.py:200-209` 打印，并写入 `{log_path}/all_results.txt` | `eval_main.py` 已纳入；写文件的 `SummaryLogger`（`agentboard/utils/logging/logger.py`）未纳入 |
| 逐 sample 的轨迹、逐步 prompt 与 usage | `agentboard/tasks/pddl.py:171` 与 `:184` 调 `agentboard.log_example(...)`，最终落到 `TaskLogger.save_sample_data_to_file_*` | 调用点已纳入；实现未纳入 |
| 机制是否按预期切块 / 摘要 | 无独立检查；只能读 `agentboard/agents/cme_final.py:114-174` 的序列化逻辑，或打印 `make_prompt` 输出（`cme_final.py:243` 会 print 完整 prompt） | 已纳入 |
| 子目标与检索是否符合协议 | 无自动检查；靠 `cme_final.py:303-326` 的字符串匹配 | 已纳入 |

## 当前核验状态

| 项目 | 状态 | 依据等级 |
| --- | --- | --- |
| PDF 可解析、页码标记完整 | 已通过，20 页 | 本地核对 |
| 论文 §3.1–3.4（机制）、§4.1–4.2、§5.1–5.5、Appendix B–C | 已与 `paper/paper-v1.txt` 逐条核对 | 本地核对 |
| Table 1–4 数值转录 | 已核对（上表） | 论文报告 |
| 正文与表格的数字不一致（§5.1 vs Table 2） | 已发现并记录，未判断哪一方为准 | 论文报告 |
| 官方代码 revision | 已固定为 `cebdd8e4eacec1a532ce2c0041db8902217b90ba`（2026-04-15），按内容比对确定 | 本地核对 |
| 机制代码路径（切块 / 摘要 / 检索 / 截断） | 已逐行阅读并给出 `文件:行号` | 代码行为 |
| `retrieve(...)` 递归返回值未被采用、快照内无任何环境拦截 `retrieve(` | 已发现，标注为读码结论 | 代码行为 |
| 官方配置的生效值（`--agent`、`--max_num_steps`、`EVALTASK` 覆盖 YAML） | 已确认 | 代码行为 |
| Context Efficiency 指标的计算脚本 | **未知**：论文报告该指标，但仓库快照中没有对应实现 | 缺失 |
| 官方端到端实验复跑 | **尚未执行**：缺 `agentboard/environment/`、`data/*.jsonl`、OpenAI 访问与 `utils/logging/` | 未执行 |
| 论文 Table 1–4 数值的独立复现 | **尚未执行** | 未执行 |
| 迁移到目标 Harness 的收益 | **尚未验证**：论文未给出脱离 AgentBoard 的接入方式 | 未执行 |
| 上游仓库是否存在更新的修复版本 | `main` 分支 HEAD 即为所固定的 revision（2026-10-05 快照时点） | 本地核对 |
