# 实现依据

`code/adaptive_plan.py` 把论文的两级自适应做成可运行实现：

| 论文环节 | 本仓库实现 | 说明 |
| --- | --- | --- |
| 计划状态 | `Plan`（`steps` / `completed` / `revisions`） | 支持取下一步、标记完成与修订留痕。 |
| in-plan 反馈 | `Plan.revise_in_plan(index, replacement, why)` | 计划形状成立、个别参数错误时只改这一步。 |
| out-of-plan 反馈 | `Plan.replan_remaining(current, replacement, why)` | 世界与计划假设冲突时丢弃未完成后缀，并清理失效的完成标记。 |
| 反馈来源 | `parse_feedback(observation, action)` | 返回 `mode` 与建议；真实系统里由模型判断，本地用正则占位。 |
| 执行环境 | `MiniHouse` | 确定性状态机，能产生「参数不符」与「前提不成立」两类反馈。 |
| 对照 | `run(..., adapt=False)` | 不自适应基线在同一任务上失败，用于说明修订的必要性。 |

该状态表示供后续 trace 与 verifier 使用；本模块不负责生成计划文本（那是执行模型的事）。
