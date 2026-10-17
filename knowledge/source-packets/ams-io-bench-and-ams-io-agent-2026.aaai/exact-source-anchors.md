# Exact source anchors

## Selected mechanism

In this paper, we propose AMS-IO-Agent, a domain-specialized LLM-based agent for structure-aware input/output (I/O) subsystem generation in analog and mixed-signal (AMS) integrated circuits (ICs).

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-aaai2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-aaai2026.txt` marker `===== PDF p.1 =====` | Design |
| Experimental setup | PDF p.2; `paper/paper-aaai2026.txt` marker `===== PDF p.2 =====` | Experiments |
| Results and ablations | PDF p.6; `paper/paper-aaai2026.txt` marker `===== PDF p.6 =====` | Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/tools/example_search_tool.py:13` | `list_examples` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/example_search_tool.py:25` | `search_examples` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/example_search_tool.py:90` | `get_example_description` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_generated/fibonacci_sequence.py:11` | `fibonacci_sequence` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_generated/read_skill_file.py:11` | `read_skill_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_generated/save_json_file.py:11` | `save_json_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_generated/create_text_file.py:11` | `create_text_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agent_generated/save_json_with_directory.py:11` | `save_json_with_directory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/tool_utils.py:10` | `_stringify` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/tool_utils.py:21` | `format_tool_logs` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/tool_utils.py:30` | `dual_stream_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/user_profile_tool.py:18` | `get_profile_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/user_profile_tool.py:37` | `read_profile` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/user_profile_tool.py:69` | `update_user_profile` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/task_query_tool.py:12` | `view_recent_tasks` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/task_query_tool.py:49` | `analyze_task_failures` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/task_query_tool.py:86` | `get_task_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/tool_stats_tool.py:12` | `get_tool_statistics` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `046a2e3edccd76322ab3e47c4dd9a5a1eded1e8a`. Paper page numbers refer to the fixed local proceedings PDF.
