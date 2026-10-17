# Exact source anchors

## Selected mechanism

Replay realistic multi-turn tool-use interactions and score orchestration, implicit intent, and instruction transitions.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | design |
| Experimental setup | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | 4 Experiments |
| Results and ablations | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | 2. Analysis |
| Limitations or failure conditions | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | 5 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/multi-agent-framework/agent/checker_tool.py:7` | `rule_checker_zh` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/checker_tool.py:31` | `rule_checker_en` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/checker_tool.py:55` | `checker_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/tool.py:80` | `tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/user_single_tool.py:77` | `user_single_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/user_multi_tool_parallel.py:103` | `user_multi_tool_parallel` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/user_multi_tool_serial_parallel.py:101` | `user_multi_tool_serial_parallel` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/user_multi_tool.py:101` | `user_multi_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/checker_planner.py:86` | `rule_checker_zh` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/checker_planner.py:218` | `rule_checker_en` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/checker_planner.py:350` | `llm_parallel_checker` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/planner.py:243` | `planner` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/agent_ask.py:58` | `agent_ask` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/user_chat.py:68` | `parse_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/user_chat.py:78` | `user_chat` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/agent_answer_chat.py:56` | `agent_answer_chat` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/agent_answer.py:60` | `agent_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/multi-agent-framework/agent/user_vague_answer_ask.py:65` | `user_vague_answer_ask` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `69647d60b990b169267598573d91fdc00ba69bfb`. Paper page numbers refer to the fixed local proceedings PDF.
