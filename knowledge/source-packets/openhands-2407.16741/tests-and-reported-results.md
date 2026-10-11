# Tests and reported results

## 论文报告结果

以下数值为论文结果，不是本仓库复跑结果。页码为 PDF 实际页。

| Benchmark | 设置 | 结果（论文） | 位置 |
| --- | --- | --- | --- |
| SWE-Bench Lite | 300 instances, w/o Hint | CodeActAgent v1.8 + claude-3-5-sonnet@20240620 = 26.0%（$1.10/例）；gpt-4o-2024-05-13 = 22.0%（$1.72） | Table 4, p.8（Table 3 p.7 同值；§4.2 p.7 正文写 "resolve rate of 26%"） |
| HumanEvalFix | 164 instances，0-shot | CodeActAgent v1.5, gpt-4o = 79.3% | Table 4, p.8 |
| WebArena | 812 instances | BrowsingAgent v1.0 claude-3-5-sonnet = 15.5%；CodeActAgent v1.8 经委托 = 15.3% | Table 5, p.9 |
| MiniWoB++ | 125 envs | BrowsingAgent gpt-4o = 40.8% | Table 5, p.9 |
| GAIA | L1 validation，53 instances | OH GPTSwarm v1.0 gpt-4o = 32.1%（$0.050） | Table 6, p.10 |
| GPQA diamond | 198 instances | CodeActAgent v1.8 claude = 52.0% / 53.1% | Table 6, p.10 |
| AgentBench OS | 144 instances | 57.6% | Table 6, p.10 |

引用注意：Tab.3（p.7）与 Tab.4（p.8）对 gpt-4o-mini 的 SWE-Bench Lite 数值不一致（6.3 vs 7.0），引用时需注明表号。15 个 benchmark 的完整清单见 Table 2（p.6）。

## 官方检查入口

| 检查对象 | 官方代码 |
| --- | --- |
| 事件流落盘与编号 | `official-code/openhands/events/stream.py:158-186` |
| 轨迹回放 | `official-code/openhands/controller/replay.py:9-82`（ReplayManager） |
| 委托链追踪 | `official-code/openhands/controller/agent_controller.py:655`（start_delegate）、`official-code/openhands/events/action/agent.py:86` |
| 评测参数 | `official-code/openhands/core/config/utils.py:494-499`（默认输出目录 `evaluation/evaluation_outputs/outputs`） |

评测脚本本体不在本快照（无 `evaluation/` 目录；`find -iname '*eval*'/*bench*'` 为空）。SWE-bench、WebArena、MiniWoB++、GAIA 的评测需从 OpenHands 主仓库单独获取。

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，38 页。 |
| 论文锚点与本地全文核对 | 已通过（Table 3/4/5/6 与正文逐项核对；Table 3 vs Table 4 的口径差已标注）。 |
| 官方代码版本与核心文件 | 已固定并保存。 |
| 大型数据与完整 benchmark 环境 | 未纳入来源包（无 evaluation/ 目录与评测脚本）。 |
| 官方端到端实验复跑 | 尚未执行（需完整上游仓库与 Docker 环境）。 |
| 迁移到目标 Harness 的收益 | 尚未验证。 |
