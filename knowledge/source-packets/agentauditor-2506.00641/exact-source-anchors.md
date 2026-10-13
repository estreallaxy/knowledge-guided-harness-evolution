# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.1，`paper/paper-v3.txt` 中的 `===== PDF p.1 =====` | `framework` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.7，`paper/paper-v3.txt` 中的 `===== PDF p.7 =====` | `5 Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.9，`paper/paper-v3.txt` 中的 `===== PDF p.9 =====` | `5.3 Ablation` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.3，`paper/paper-v3.txt` 中的 `===== PDF p.3 =====` | `limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `AgentAuditor/__init__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/__main__.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/cluster.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/demo.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/demo_repair.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/direct_eval.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/direct_metric.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/eval.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/infer.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/infer_emb.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/infer_fix1.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `AgentAuditor/tasks/infer_fix2.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
