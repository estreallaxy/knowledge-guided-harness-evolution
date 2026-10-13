# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 实验设置 | PDF p.7，`paper/paper-v2.txt` 中的 `===== PDF p.7 =====` | `4 Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.7，`paper/paper-v2.txt` 中的 `===== PDF p.7 =====` | `analysis` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.3，`paper/paper-v2.txt` 中的 `===== PDF p.3 =====` | `limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `mm_agents/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `mm_agents/agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `mm_agents/aguvis_agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `mm_agents/uitars_agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `judge/methods/aer.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `judge/methods/all_step_aer.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `judge/methods/plain_judge.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `mm_agents/accessibility_tree_wrap/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `mm_agents/accessibility_tree_wrap/heuristic_retrieve.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `mm_agents/accessibility_tree_wrap/relevant_retrieve.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `mm_agents/gui_som/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `mm_agents/gui_som/data_preparation/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
