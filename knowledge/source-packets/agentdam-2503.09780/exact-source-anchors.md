# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 实验设置 | PDF p.8，`paper/paper-v3.txt` 中的 `===== PDF p.8 =====` | `4 Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.7，`paper/paper-v3.txt` 中的 `===== PDF p.7 =====` | `results` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.20，`paper/paper-v3.txt` 中的 `===== PDF p.20 =====` | `limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `agentdam/privacy_eval.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `agentdam/run_agentdam.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `agentdam/prepare.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `visualwebarena/setup.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `agentdam/croissant/generate_croissant_metadata.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `agentdam/llama3x/llama_test_vllm.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `agentdam/llama3x/run_llama3_vllm_localhost.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
