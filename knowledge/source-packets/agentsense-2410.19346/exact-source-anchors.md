# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.3，`paper/paper-v2.txt` 中的 `===== PDF p.3 =====` | `3.1 Framework` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.6，`paper/paper-v2.txt` 中的 `===== PDF p.6 =====` | `4 Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.15，`paper/paper-v2.txt` 中的 `===== PDF p.15 =====` | `results` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.9，`paper/paper-v2.txt` 中的 `===== PDF p.9 =====` | `Limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `SENSE/initialization.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `SENSE/metric.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `SENSE/run_eval.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `SENSE/simulation.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `SENSE/commands/example/gpt4o.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `SENSE/commands/example/heter_gpt4o_gpt35.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `SENSE/commands/example/llama3_8b.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `SENSE/configs/judge_config.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `SENSE/configs/prompt_template.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `data_prepare/process_example.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `data_prepare/1_goal/llm.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `data_prepare/2_private_info/05_validate_info.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
