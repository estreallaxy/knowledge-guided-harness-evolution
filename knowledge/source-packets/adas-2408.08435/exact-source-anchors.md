# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.4，`paper/paper-v2.txt` 中的 `===== PDF p.4 =====` | `approach` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.3，`paper/paper-v2.txt` 中的 `===== PDF p.3 =====` | `experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.6，`paper/paper-v2.txt` 中的 `===== PDF p.6 =====` | `Results` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| 文件 | 核对范围 |
| --- | --- |
| `LICENSE` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `README.md` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `requirements.txt` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `dataset/GSM8k_test.jsonl` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `dataset/readme.md` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `results/mgsm_transfer_domains_results.json` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `_arc/arc_prompt.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `_drop/drop_prompt.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |

代码位置均以 `source-packet.json` 固定的上游 revision 为准；论文页码以本地 PDF 为准。
