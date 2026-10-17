# Exact source anchors

## Selected mechanism

To systematically scale safety testing in multi-turn, tool-realistic settings, we propose a principled taxonomy that transforms single-turn harmful tasks into multi-turn attack sequences.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | system |
| Results and ablations | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agentrisk/db_setup.py:9` | `reset_postgres_db` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentrisk/post_eval.py:81` | `gather_task_description` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentrisk/post_eval.py:100` | `load_artifacts` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentrisk/post_eval.py:113` | `load_artifacts_with_fallback` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentrisk/run_eval.py:86` | `TurnConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentrisk/run_eval.py:94` | `TurnManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentrisk/run_eval.py:317` | `SingleTurnUser` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/_paths.py:12` | `repo_root` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/_paths.py:20` | `default_agent_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/_paths.py:25` | `default_eval_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/experience_store.py:17` | `ExperienceStore` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/experience_store.py:138` | `load_experiences` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentrisk/reset_notion.py:23` | `find_ghost_page` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentrisk/reset_notion.py:42` | `full_reset` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/inspector.py:14` | `_parse_sse_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/inspector.py:27` | `MCPStreamableHTTPInspector` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/inspector.py:80` | `MCPSSEInspector` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolshield/mcp_scan.py:30` | `is_port_open` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `95a2e342492f10e1a61e5c3bcb8df1149005560f`. Paper page numbers refer to the fixed local proceedings PDF.
