# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.5，`paper/paper-v1.txt` 中的 `===== PDF p.5 =====` | `Method` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.2，`paper/paper-v1.txt` 中的 `===== PDF p.2 =====` | `Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.6，`paper/paper-v1.txt` 中的 `===== PDF p.6 =====` | `4.3 Analysis` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.5，`paper/paper-v1.txt` 中的 `===== PDF p.5 =====` | `3.4 Discussion` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `AgentDropout/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/agents/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/agents/adversarial_agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/agents/agent_registry.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/agents/analyze_agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/agents/code_writing.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/agents/final_decision.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/agents/math_solver.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/agents/math_solver_aqua.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/domain/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/graph/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentDropout/graph/graph.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
