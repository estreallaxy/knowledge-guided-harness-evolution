# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.8，`paper/paper-v1.txt` 中的 `===== PDF p.8 =====` | `50 framework` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.6，`paper/paper-v1.txt` 中的 `===== PDF p.6 =====` | `4 Experiment Setup` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.7，`paper/paper-v1.txt` 中的 `===== PDF p.7 =====` | `5 Ablation` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.4，`paper/paper-v1.txt` 中的 `===== PDF p.4 =====` | `Discussion` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `marble/main.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `marble/engine/engine_planner.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `marble/graph/agent_graph.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `marble/evaluator/env_evaluation_prompts.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `marble/evaluator/evaluator_prompts.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `multiagentbench/jsonl2yaml.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `multiagentbench/runjsonl2yaml.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tests/test_model_prompting.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tests/test_short_term_memory.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `marble/agent/base_agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `marble/agent/werewolf_agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `marble/agent/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
