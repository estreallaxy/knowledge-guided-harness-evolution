# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.3，`paper/paper-v4.txt` 中的 `===== PDF p.3 =====` | `Framework` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.4，`paper/paper-v4.txt` 中的 `===== PDF p.4 =====` | `Results` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| 文件 | 核对范围 |
| --- | --- |
| `scripts/eval/m3tooleval/main.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/eval/m3tooleval/run.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/eval/science-world/slow_agent/run_gradio.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/docker/run_megatron_interactive.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/docker/run_megatron_interactive_slurm.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/eval/run_all.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/eval/api-bank/demo.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/eval/api-bank/run.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/eval/miniwob++/main.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `scripts/data/interaction/collection/run_mint_docker_interactive.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |

代码位置均以 `source-packet.json` 固定的上游 revision 为准；论文页码以本地 PDF 为准。
