# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 实验设置 | PDF p.6，`paper/paper-v2.txt` 中的 `===== PDF p.6 =====` | `4 Experiments` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.2，`paper/paper-v2.txt` 中的 `===== PDF p.2 =====` | `Analysis` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 限制与边界 | PDF p.10，`paper/paper-v2.txt` 中的 `===== PDF p.10 =====` | `Limitations` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| 文件 | 核对范围 |
| --- | --- |
| `agentboard/eval_main.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `agentboard/environment/WebShop/run_dev.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `agentboard/environment/WebShop/run_web_agent_site_env.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `agentboard/environment/WebShop/run_web_agent_text_env.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `agentboard/environment/pddl_env/pddlgym/demo.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `agentboard/environment/pddl_env/pddlgym/demo_planning.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `agentboard/environment/WebShop/search_engine/run_indexing.sh` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |
| `agentboard/environment/WebShop/web_agent_site/app.py` | 官方仓库固定 revision 中的实现、接口或配置入口；具体语义以文件内容为准。 |

代码位置均以 `source-packet.json` 固定的上游 revision 为准；论文页码以本地 PDF 为准。
