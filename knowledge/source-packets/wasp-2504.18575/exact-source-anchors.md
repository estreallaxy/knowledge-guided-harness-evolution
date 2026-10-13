# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.9，`paper/paper-v3.txt` 中的 `===== PDF p.9 =====` | `framework` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.6，`paper/paper-v3.txt` 中的 `===== PDF p.6 =====` | `4 Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.7，`paper/paper-v3.txt` 中的 `===== PDF p.7 =====` | `4.2 Results` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.9，`paper/paper-v3.txt` 中的 `===== PDF p.9 =====` | `Limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `webarena_prompt_injections/constants.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/environment_cleanup.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/environment_setup.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/evaluator_step_by_step.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/evaluator_step_by_step_utils.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/prompt_injector.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/requirements.txt` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/run.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/setup.sh` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/utils.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/environment_editors/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `webarena_prompt_injections/environment_editors/base_environment_editor.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
