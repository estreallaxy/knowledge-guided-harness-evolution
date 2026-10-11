# Exact source anchors

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| ConversableAgent 自动回复（角色系统提示 + 共享历史） | §2.1、§2.2 设计模式 1，PDF p.3、p.5（Figure 2 p.4） | 支持：每个 agent 有 send/receive/generate_reply 统一接口与内部上下文；收到消息后自动调用回复并回送 sender，除非触发终止条件；内置 LLM/代码/人类回复函数，可注册自定义回复函数（"auto-reply mechanism" p.5）。不支持：论文未写 API 名与函数级细节。 |
| GroupChat/GroupChatManager 自动选发言者 | §2.2 p.5；§3 A5 p.9；附录 B.1 p.16；附录 D A5 p.28（Figure 12 p.28） | 支持：Manager 循环三步——动态选 speaker、请其发言、把回复广播给其他所有 agent；选人用 role-play 提示，论文对比 role-play 与 task-based 策略（p.28）。不支持：论文未给 select_speaker 函数名与回退规则（属代码）。 |
| 嵌套会话（nested chats） | §2.2 p.5；附录 D A1 Scenario 3 p.21；§3 A6 p.30 | 支持（语义层面）：定制 generate reply 函数内，一个 agent 可保持当前会话、同时依消息与上下文触发与其他 agent 的对话（p.5）；Scenario 3 的 ask_for_expert 子对话（p.21）；A6 中玩家与 board agent 的对话对其他玩家不可见（p.30）。未定位：v2 全文无 "nested/sub-conversation" 术语，register_nested_chats API 不在本期代码。 |
| 代码执行器（代码块抽取与执行；local/docker） | §2.1 p.3；§2.2 p.5 | 支持：Tool-backed agent 可通过代码执行/函数执行使用工具；默认 UserProxyAgent 能执行 LLM 建议的代码并把结果作为反馈回传（p.3、p.5）。不支持：论文正文未给 local vs docker、超时、镜像等细节（在代码中）。 |
| 终止条件与 human-in-the-loop | §2.1 p.3；§2.2 p.5；附录 B.1 p.16–17；附录 D A1 Scenario 2 p.20–21 | 支持：可指定 termination condition、human input mode、最大 auto-reply 次数；人类可跳过输入（p.3）；实践建议开发期 'ALWAYS'、稳定后 'NEVER'（p.16–17）；Scenario 2 只设 ALWAYS 即接入人工提示（p.20–21）。三值枚举细节在代码与 Figure 2（p.4）。 |
| 评测：MATH + Table 2 | 附录 D A1 p.19–20（Table 2 p.19）；Figure 4a p.7 | 支持：Table 2（每题 3 次定性）AutoGen 第一题 3/3、第二题 2/3；对照最差为 AutoGPT 0/3、LangChain ReAct 0/3 等。正文 p.20：全量 MATH（5000 题）AutoGen 69.48% vs GPT-4 55.18%；另测 120 道 level-5。 |
| 评测：NQ / ALFWorld / OptiGuide（A2–A4） | 附录 D p.22–27；Figure 4b–d p.7 | 支持：NQ 无交互检索版前 500 题 F1 23.40%/Recall 62.60%，19.4% 问题触发 Update Context（p.23）；ALFWorld 134 unseen：ALFChat-3 avg 69 / best-of-3 77（Table 3 p.25）；OptiGuide 多 agent 识别不安全代码 F1 +8%（GPT-4）/ +35%（GPT-3.5）（p.8）；交互节省 3.03x–4.88x（Table 4 p.27）；代码 430→100 行（p.8/p.26）。 |
| 评测：A5 动态群聊 / A7 MiniWob++ | 附录 D A5 p.28（Table 5、6）；A7 p.32–33（Figure 18、Table 7 p.33） | 支持：12 个手工任务：GPT-4 群聊成功 11/12、两 agent 9、task-based 8；GPT-3.5 9/8/7（Table 5）；平均 LLM 调用/终止失败见表 6（p.28）。MiniWob++（49 任务）成功率 52.8%，仅比 RCI 低 3.6%（p.32）。论文未使用 HumanEval（全词 0 命中）。 |
| 限制/边界 | §4 p.10；附录 B.2 p.17；Ethics p.10；附录 C p.18 | 支持：作者自述"仍处早期实验阶段"（p.10）；agent 数量/自由度增加带来新安全挑战（p.10）；工作流复杂后难记录与调试，可能退化为 "incomprehensible, unintelligible chatter"（p.17）；高风险场景需 fail-safe 与人类监督（p.17）；代码执行/装包类外部改动有风险（p.10）。 |

## 官方代码

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| 自动回复主循环（收消息→生成→回送） | `official-code/autogen/agentchat/conversable_agent.py:430-464`（receive 内 459-464 调用 generate_reply 并 send）；`291-338`（send） | 对应论文 "auto-reply mechanism"：除终止外每条消息都触发回复。 |
| 回复函数注册与顺序（LLM/代码/函数/人类） | `official-code/autogen/agentchat/conversable_agent.py:126-129`（默认注册四项）；`131-183`（register_reply）；`733-782`（generate_reply 依序调用，782 兜底 default_auto_reply） | 论文 "built-in reply functions + register custom reply" 的实现面。 |
| 发起对话 + 角色系统提示 + 共享历史 | `official-code/autogen/agentchat/conversable_agent.py:510-531`（initiate_chat）；`592-609`（generate_oai_reply，607 拼接 `self._oai_system_message + messages`） | 对应"角色系统提示 + 共享历史"。 |
| GroupChat 发言者选择（role-play + 回退） | `official-code/autogen/agentchat/groupchat.py:9-63`（select_speaker_msg 34-40；select_speaker 42-60，54-60 失败回退 next_agent）；max_round 默认 10（:14） | 对应论文 role-play speaker selection（p.28）；LLM 失败轮转属实现补充。 |
| GroupChatManager 编排（选人→发言→广播） | `official-code/autogen/agentchat/groupchat.py:66-133`（87 register_reply；run_chat 90-133：广播 107-110、select_speaker 116、generate_reply 118、KeyboardInterrupt 由 admin 发言 119-127） | 对应 Figure 12 三步与附录 B.1 p.16。 |
| 代码块抽取与执行（local/docker） | `official-code/autogen/agentchat/conversable_agent.py:611-643`（generate_code_execution_reply）、`885-925`（execute_code_blocks）；`official-code/autogen/code_utils.py:21`（CODE_BLOCK_PATTERN）、`48-84`（extract_code）、`216-393`（execute_code；221 `use_docker` 默认随 docker 包） | 对应论文代码执行/工具能力；docker 需 daemon，否则需 `use_docker: False` 本机执行。 |
| 终止条件与人类输入模式 | `official-code/autogen/agentchat/conversable_agent.py:662-731`（check_termination_and_human_reply）；`:54` human_input_mode 默认 "TERMINATE"；`:46` MAX_CONSECUTIVE_AUTO_REPLY=100；`official-code/autogen/agentchat/user_proxy_agent.py:23` 默认 "ALWAYS"；`official-code/autogen/agentchat/assistant_agent.py:36` 默认 "NEVER" | 对应论文 termination/human_input_mode 机制。 |
| 子类默认与系统提示（对应附录 C） | `official-code/autogen/agentchat/assistant_agent.py:16-27`（DEFAULT_SYSTEM_MESSAGE）；`official-code/autogen/agentchat/user_proxy_agent.py:5-16`（默认 ALWAYS、llm_config=False、代码执行默认开） | 与论文 Figure 5/p.18 系统提示对照（论文标 v0.1.1，代码 0.1.6）。 |
| 嵌套会话 API（未定位） | 全快照 `grep -rn 'nested'` 无命中；仅有 initiate_chat:510 / a_initiate_chat:533，无 register_nested_chats | 本期 revision 未实现嵌套聊天 API；论文侧语义见上表第 3 行。 |

行号以 `source-packet.json` 固定的官方代码 revision 为准。
