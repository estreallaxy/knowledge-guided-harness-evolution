# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.2，`paper/paper-v1.txt` 中的 `===== PDF p.2 =====` | `method` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.12，`paper/paper-v1.txt` 中的 `===== PDF p.12 =====` | `results` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.8，`paper/paper-v1.txt` 中的 `===== PDF p.8 =====` | `Limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `evaluation/evaluation.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `api_docs/DeveloperTools/apicagent.txt` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `api_docs/DeveloperTools/cloudflaretrace.txt` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/DeveloperTools/apicagent.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/DeveloperTools/cloudflaretrace.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/Language/chinesetext.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/Language/datamuse.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/Language/freedictionary.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/Language/purgomalum.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/Music/binaryjazz.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/Music/musicbrainz.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `tools/Music/openwhyd.json` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
