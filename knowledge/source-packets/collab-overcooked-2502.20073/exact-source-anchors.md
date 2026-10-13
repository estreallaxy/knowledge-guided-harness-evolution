# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.2，`paper/paper-v3.txt` 中的 `===== PDF p.2 =====` | `approach` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.9，`paper/paper-v3.txt` 中的 `===== PDF p.9 =====` | `Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.2，`paper/paper-v3.txt` 中的 `===== PDF p.2 =====` | `analysis` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `src/main.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/collab/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/collab/collab.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/collab/modules.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/collab/utils.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/collab/web_util.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `lib/overcooked_ai/overcooked_ai_py/planning/planners.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/prompts/gpt/assistant_example.txt` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/prompts/gpt/chef_example.txt` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/prompts/gpt/reflection_rule.txt` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/prompts/reference/5_mashed_broccoli_and_bean_patty_ref.txt` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `src/prompts/reference/5_mashed_carrot_and_chickpea_patty_ref.txt` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
