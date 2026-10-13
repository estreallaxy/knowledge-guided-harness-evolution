# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.3，`paper/paper-v1.txt` 中的 `===== PDF p.3 =====` | `3 Method` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.7，`paper/paper-v1.txt` 中的 `===== PDF p.7 =====` | `experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.7，`paper/paper-v1.txt` 中的 `===== PDF p.7 =====` | `results` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.5，`paper/paper-v1.txt` 中的 `===== PDF p.5 =====` | `limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `8.1construct_refinetoolbench_apicalling.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `8.2construct_refinetoolbench_apitrace.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `8.3get_refinetoolbench.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `8.4evalute_refinetoolbench.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `stabletoolbench/server/main_refinetoolbench.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `stabletoolbench/toolbench/inference/Algorithms/multi_agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `stabletoolbench/server/main.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `stabletoolbench/server/main_backup.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `stabletoolbench/server/utils.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `stabletoolbench/toolbench/tool_conversation.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `stabletoolbench/toolbench/utils.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `stabletoolbench/toolbench/inference/qa_pipeline.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
