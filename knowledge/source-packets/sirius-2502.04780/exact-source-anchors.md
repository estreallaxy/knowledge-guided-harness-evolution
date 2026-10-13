# Exact source anchors

## 论文

| 核对对象 | 精确位置 | 可支持的判断 |
| --- | --- | --- |
| 方法与系统设计 | PDF p.7，`paper/paper-v1.txt` 中的 `===== PDF p.7 =====` | `Method` 所在页；用于核对该部分的原始定义、条件与证据。 |
| 结果与消融 | PDF p.5，`paper/paper-v1.txt` 中的 `===== PDF p.5 =====` | `results` 所在页；用于核对该部分的原始定义、条件与证据。 |

## 官方代码

| Method 实现 | 核对范围 |
| --- | --- |
| `Actor_Critic/agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Actor_Critic/prompt.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Actor_Critic/prompt_critic.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/agent.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/NegotiationArena/negotiationarena/agent_message.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/NegotiationArena/games/buy_sell_game/prompt.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/NegotiationArena/games/simple_game/prompt.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/NegotiationArena/games/trading_game/prompt.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/NegotiationArena/games/ultimatum/prompt.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/NegotiationArena/negotiationarena/agents/agents.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/NegotiationArena/negotiationarena/agents/agent_behaviours.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |
| `Competitive/NegotiationArena/negotiationarena/agents/chatgpt.py` | 与论文核心机制直接对应的方法实现或调用入口；核对其输入、状态转换、输出与依赖。 |

代码位置均以 `source-packet.json` 固定的官方代码 revision 为准；论文页码以本地 PDF 为准。
