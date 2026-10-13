# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.3，`paper/paper-v1.txt` 中的 `===== PDF p.3 =====` | `3 Methodology` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.5，`paper/paper-v1.txt` 中的 `===== PDF p.5 =====` | `4.2 Experiment Setup` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.2，`paper/paper-v1.txt` 中的 `===== PDF p.2 =====` | `results` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.9，`paper/paper-v1.txt` 中的 `===== PDF p.9 =====` | `Limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `check_knowledge_capabilities.ipynb` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `compute_LLMscore.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `llm_eval.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `utils.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
