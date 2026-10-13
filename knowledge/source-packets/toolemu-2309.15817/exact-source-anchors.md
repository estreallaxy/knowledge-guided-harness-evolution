# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.14，`paper/paper-v2.txt` 中的 `===== PDF p.14 =====` | `approach` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.11，`paper/paper-v2.txt` 中的 `===== PDF p.11 =====` | `failure` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| 文件 | 核对范围 |
| --- | --- |
| `scripts/run.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |

代码位置均以 `source-packet.json` 固定的上游 revision 为准；论文页码以本地 PDF 为准。
