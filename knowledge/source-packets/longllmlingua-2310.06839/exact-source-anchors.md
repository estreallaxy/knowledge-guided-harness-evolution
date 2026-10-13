# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.5，`paper/paper-v2.txt` 中的 `===== PDF p.5 =====` | `method` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 实验设置 | PDF p.5，`paper/paper-v2.txt` 中的 `===== PDF p.5 =====` | `5 Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.6，`paper/paper-v2.txt` 中的 `===== PDF p.6 =====` | `results` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| 文件 | 核对范围 |
| --- | --- |
| `experiments/securitylingua/run.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/securitylingua/train_roberta.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/llmlingua2/evaluation/eval_bbh.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/llmlingua2/evaluation/eval_gsm8k.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/llmlingua2/evaluation/eval_longbench.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/llmlingua2/evaluation/eval_meetingbank_qa.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/llmlingua2/evaluation/eval_meetingbank_summary.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/llmlingua2/evaluation/eval_zero_scrolls.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/llmlingua2/model_training/train.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `experiments/llmlingua2/model_training/train_roberta.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |

代码位置均以 `source-packet.json` 固定的上游 revision 为准；论文页码以本地 PDF 为准。
