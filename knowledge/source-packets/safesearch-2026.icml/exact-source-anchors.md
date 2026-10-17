# Exact source anchors

## Selected mechanism

To study this threat systematically, we propose SafeSearch, an automated red-teaming framework that is scalable, cost-efficient, and lightweight, enabling sandboxed safety evaluation of search agents.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | experiments |
| Results and ablations | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/executor_with_search_agents.py:46` | `SearchAgentExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/executor_with_search_agents.py:627` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/executor_with_search_agents.py:753` | `_prepare_generation_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/search/tool.py:26` | `WebSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/tool_calling_loop.py:44` | `fetch_client_and_model_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/tool_calling_loop.py:52` | `ToolCallingLoop` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/tools_and_schemas.py:5` | `SearchQueryList` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/tools_and_schemas.py:14` | `Reflection` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/state.py:15` | `OverallState` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/state.py:24` | `ReflectionState` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/state.py:32` | `Query` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/prompts.py:5` | `get_current_date` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/graph.py:40` | `generate_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/graph.py:65` | `continue_to_web_research` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/graph.py:77` | `web_research` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/configuration.py:9` | `Configuration` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent/deepmind_agent/configuration.py:84` | `load_configuration` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/search_required_check.py:8` | `remove_thinking_contents` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `27f2084fe9c6544a024fb422e84e6893b66230bc`. Paper page numbers refer to the fixed local proceedings PDF.
