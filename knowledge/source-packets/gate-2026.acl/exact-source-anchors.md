# Exact source anchors

## Selected mechanism

To address these challenges, we propose GATE (Graph-based Adaptive Tool Evolution), an adaptive framework that dynamically constructs and evolves a hierarchical graph of reusable tools across multiple scenarios.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | framework |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 6 Analysis |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 9 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent/environment/notebook.py:5` | `Notebook` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/environment/code.py:4` | `extract_code_pieces` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/environment/code.py:24` | `wrap_code` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/environment/code.py:30` | `unwrap_code` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/environment/utils.py:16` | `timeout` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/environment/utils.py:31` | `extract_function_head` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/environment/utils.py:50` | `extract_tool_used` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/environment/env.py:58` | `Env` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/memory.py:9` | `Memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/action/toolagent_action.py:6` | `Retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/action/toolagent_action.py:53` | `CreateTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/action/toolagent_action.py:112` | `EditTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/config.py:5` | `Config` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/config.py:23` | `LLMConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/config.py:40` | `AgentConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_test.py:10` | `StreamToLogger` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_test.py:26` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/llm.py:10` | `LLMCallException` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `0756fccca491f6494d264084e0f38a17de5c1b39`. Paper page numbers refer to the fixed local proceedings PDF.
