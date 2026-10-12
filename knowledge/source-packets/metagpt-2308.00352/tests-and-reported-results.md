# Tests and reported results

## 论文报告结果

以下数值为论文结果，不是本仓库复跑结果。页码为 PDF 实际页。

| 实验 | 设置 | 结果（论文） | 位置 |
| --- | --- | --- | --- |
| HumanEval / MBPP | MetaGPT+GPT-4 Pass@1 | 85.9 / 87.7 | Fig.4 p.7 与正文（无对应数值表） |
| SoftwareDev 主结果 | 70 任务 | Executability 3.75→；Tokens 31,255；Productivity 124.3；Human Revision Cost 0.83 | Table 1, p.8 |
| 可执行反馈消融 | HumanEval/MBPP Pass@1 | +4.2% and +5.4%（w/o 反馈 81.7/82.3 → 85.9/87.7） | §4.4 p.9、Fig.4 p.7 |
| 角色数消融 | SoftwareDev | 1 agent：1.0 executability / 10 revisions / $0.915 → 4 角色：4.0 / 2.5 / $1.385；#Lines 83→191 | Table 3, p.9 |
| 跨框架比较 | 7 任务 executability | MetaGPT 3.9 vs ChatDev 2.1、其余 1.0 | Table 4, p.24 |
| w/o Feedback 明细 | 70 任务 Avg | 26,626.86+6,218 tokens、516.71 s、$1.12、3.36 分 | Table 9, p.29 |

引用注意：

- 85.9/87.7 只出现在 Fig.4 柱图与正文，无表格；Fig.4 中 w/o 反馈的 81.7/82.3 为 pdftotext 打散后的推定值（与 §4.4 的 +4.2/+5.4 算术吻合）。
- p.8 正文 "503 seconds" 对应 w/o-Feedback 列，Table 1 中 MetaGPT 列为 541 s；引用时勿混。
- 论文没有"去掉 SOP"的受控消融（多关键词零命中核实）。

## 官方检查入口

| 检查对象 | 官方代码 |
| --- | --- |
| 端到端生成（含 QA 反馈） | CLI `metagpt "Create a 2048 game"` 或 `generate_repo(...)`，产物在 `./workspace` |
| 测试运行与失败调试 | `official-code/metagpt/roles/qa_engineer.py:48-177`、`official-code/metagpt/actions/run_code.py:92-146`、`official-code/metagpt/actions/debug_error.py:48-74` |
| 测试文件落盘 | WriteTest 写入 `{workspace}/tests/test_*.py` |

HumanEval/MBPP 评测 harness 不在本快照内（零命中），需从上游 `examples/benchmark` 获取。

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，29 页。 |
| 论文锚点与本地全文核对 | 已通过（Table 1/3/4/9、Fig.4 与正文逐项核对；Fig.4 柱标签为旋转文本、两处数值为推定并已标注）。 |
| 官方代码版本与核心文件 | 已固定并保存。 |
| 大型数据与完整 benchmark 环境 | 未纳入来源包。 |
| 官方端到端实验复跑 | 尚未执行（快照缺 utils 等模块，需完整安装）。 |
| 迁移到目标 Harness 的收益 | 尚未验证。 |
