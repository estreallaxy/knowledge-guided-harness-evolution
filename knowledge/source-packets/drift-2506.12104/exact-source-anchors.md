# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.15，`paper/paper-v3.txt` 中的 `===== PDF p.15 =====` | `Method` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.6，`paper/paper-v3.txt` 中的 `===== PDF p.6 =====` | `4 Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.9，`paper/paper-v3.txt` 中的 `===== PDF p.9 =====` | `4.4 Ablation` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.12，`paper/paper-v3.txt` 中的 `===== PDF p.12 =====` | `Limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| 文件 | 核对范围 |
| --- | --- |
| `ASB_DRIFT/scripts/run.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `ASB_DRIFT/main_attacker.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |

代码位置均以 `source-packet.json` 固定的上游 revision 为准；论文页码以本地 PDF 为准。
