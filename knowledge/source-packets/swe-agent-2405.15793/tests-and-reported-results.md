# Tests and reported results

## 论文报告结果

以下数值为论文结果，不是本仓库复跑结果。页码为 PDF 实际页。

| 实验 | 设置 | 结果（论文） | 位置 |
| --- | --- | --- | --- |
| SWE-bench 主结果 | GPT-4 Turbo | full 12.47%（$1.59）、Lite 18.00%（$1.67） | Table 1, p.6 |
| SWE-bench 主结果 | Claude 3 Opus | full 10.46%、Lite 13.00% | Table 1, p.6 |
| Shell-only / RAG 对照 | GPT-4 Turbo / Claude 3 Opus | Shell-only Lite 11.00%（w/o demo 7.33%）；RAG 1.31/2.67% 与 3.79/4.33% | Table 1, p.6 |
| ACI 组件消融 | SWE-bench Lite | 基线（linting + Summarized + 100 行 + Last-5）= 18.0；去掉各组件后 15.0/10.3、12.0/15.7、14.3/12.7、15.0/16.3 | Table 3, p.6 |
| 超参扫描 | dev 子集 37 例 | 最佳 15.1%（T=0.0/窗口 100/Last-5）；窗口 200 显著变差 | Table 5, p.25 |
| per-repo / 年份 | GPT-4 | django 26.32%、psf/requests 33.33%、sympy 10.39%；年份间无相关性 | Table 6/7, p.26 |
| 错误类型 | 未解决轨迹 | Incorrect/Overly Specific 合计 52.0%，Failed Edit Recovery 23.4%；自动标注一致率 87% | Figure 8 p.8、Table 9 p.35 |
| 编辑失败率 | 全量轨迹 | 1185/2294（51.7%）含 ≥1 次 lint 失败编辑；任一次编辑最终成功 90.5%，失败一次后降至 57.2% | §5.2, p.8 |
| HumanEvalFix | CodeAct 类对照 | Python 87.7 / JS 89.7 / Java 87.9（三语言均值 88.3%，摘要写 87.7%） | Table 2 p.6、§5 正文 |
| pass@k | Lite | 6 次平均 17.94%（±0.49），pass@6 32.67% | Table 10, p.35 |

口径提醒：摘要 12.5%/87.7% 与正文 12.47%/88.3% 的差异来自四舍五入与均值口径；`README.upstream.md` 的 Lite 23% 为后续版本口径，晚于论文的 18.00%。

## 官方检查入口

| 检查对象 | 官方代码 |
| --- | --- |
| 批量运行 SWE-bench 实例 | `python -m sweagent.run.run run-batch --config <yaml>`（`sweagent/run/run.py:13-46`） |
| 轨迹回放 | `run-replay` 子命令（同上） |
| 轨迹产物 | `trajectories/<user>/<config>__<model>__<source>`（`official-code/sweagent/run/run_batch.py:33-43`） |

本快照内无 SWE-bench 评测脚本（判分需外部 SWE-bench harness），也无官方 tests 目录；端到端复跑未在来源包内进行。

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，118 页。 |
| 论文锚点与本地全文核对 | 已通过（Table 1/3/5/6/7、§5.2、§E.3 逐项核对；检索上限 50 vs 代码 >100 的漂移已标注）。 |
| 官方代码版本与核心文件 | 已固定并保存（含 utils/，补齐 import 依赖）。 |
| 大型数据与完整 benchmark 环境 | 未纳入来源包（无 SWE-bench harness、无 trajectories/demonstrations）。 |
| 官方端到端实验复跑 | 尚未执行（快照无 pyproject/演示轨迹，不可直接安装运行）。 |
| 迁移到目标 Harness 的收益 | 尚未验证。 |
