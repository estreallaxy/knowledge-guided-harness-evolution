# Exact source anchors

## Selected mechanism

Coordinate planner, builder, and reviewer roles through shared artifacts to synthesize and validate complex systems.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | Framework |
| Experimental setup | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | experiments |
| Results and ablations | PDF p.12; `paper/paper-iclr2026.txt` marker `===== PDF p.12 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/planning_graph.py:17` | `load_planning_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/planning_graph.py:51` | `planning_agent_node` | Pinned implementation entry for the selected mechanism. |
| `official-code/planning_graph.py:225` | `self_reflection_node` | Pinned implementation entry for the selected mechanism. |
| `official-code/agenticFL_workflow.py:23` | `load_env_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/agenticFL_workflow.py:68` | `print_banner` | Pinned implementation entry for the selected mechanism. |
| `official-code/agenticFL_workflow.py:81` | `print_section_header` | Pinned implementation entry for the selected mechanism. |
| `official-code/state.py:11` | `PlanningAgentState` | Pinned implementation entry for the selected mechanism. |
| `official-code/state.py:25` | `HumanInputState` | Pinned implementation entry for the selected mechanism. |
| `official-code/state.py:34` | `OutputState` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:43` | `web_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:82` | `search_documents` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:120` | `search_code` | Pinned implementation entry for the selected mechanism. |
| `official-code/coding_graph.py:40` | `cached_tool_invoke` | Pinned implementation entry for the selected mechanism. |
| `official-code/coding_graph.py:57` | `get_llm_instance` | Pinned implementation entry for the selected mechanism. |
| `official-code/coding_graph.py:111` | `kill_process_tree` | Pinned implementation entry for the selected mechanism. |
| `official-code/code_vecstore.py:22` | `load_repo_urls` | Pinned implementation entry for the selected mechanism. |
| `official-code/code_vecstore.py:27` | `get_repo_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/code_vecstore.py:32` | `fetch_python_files` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `58baa2b34636e53d5389525362bd75291d14073d`. Paper page numbers refer to the fixed local proceedings PDF.
