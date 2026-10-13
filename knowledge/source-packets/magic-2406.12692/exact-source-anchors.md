# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.1，`paper/paper-v3.txt` 中的 `===== PDF p.1 =====` | `method` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.2，`paper/paper-v3.txt` 中的 `===== PDF p.2 =====` | `experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.5，`paper/paper-v3.txt` 中的 `===== PDF p.5 =====` | `Results` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.7，`paper/paper-v3.txt` 中的 `===== PDF p.7 =====` | `Discussion` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `magic/guideline_generation.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `magic/multi_agent_feedback_generation.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `magic/self_correction_with_guideline.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `scripts/guideline_generation.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `scripts/multi_agent_feedback_generation.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `scripts/self_correction_with_guideline.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `utils/llm_apis.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `utils/sql_extractor.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
