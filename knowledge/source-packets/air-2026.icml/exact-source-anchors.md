# Exact source anchors

## Selected mechanism

In this work, we introduce AIR, the first incident response framework for LLM agent systems.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | framework |
| Results and ablations | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 5. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/case_studies/embodied_agent/sandbox_root/environment_state.py:15` | `ObjectType` | Pinned implementation entry for the selected mechanism. |
| `official-code/case_studies/embodied_agent/sandbox_root/environment_state.py:62` | `LocationType` | Pinned implementation entry for the selected mechanism. |
| `official-code/case_studies/embodied_agent/sandbox_root/environment_state.py:75` | `ObjectState` | Pinned implementation entry for the selected mechanism. |
| `official-code/state.py:16` | `ToolCall` | Pinned implementation entry for the selected mechanism. |
| `official-code/state.py:25` | `IncidentState` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_factory.py:16` | `create_safe_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_factory.py:143` | `create_safe_agent_with_custom_instructions` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_factory.py:226` | `create_safe_embodied_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:17` | `configure_detector` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:28` | `_extract_tool_args_from_session` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:94` | `check_for_incidents` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_wrapper.py:25` | `get_detector` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_wrapper.py:33` | `create_safe_tool_with_eradication` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_wrapper.py:398` | `check_initial_rule` | Pinned implementation entry for the selected mechanism. |
| `official-code/case_studies/embodied_agent/embodied_agent_demo.py:53` | `interactive_demo` | Pinned implementation entry for the selected mechanism. |
| `official-code/case_studies/embodied_agent/embodied_agent_demo.py:166` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/case_studies/code_agent/code_agent_demo.py:37` | `reset_sandbox` | Pinned implementation entry for the selected mechanism. |
| `official-code/case_studies/code_agent/code_agent_demo.py:81` | `python_repl_impl` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d455895f4b90610e7ee16dca5ae827a617b51044`. Paper page numbers refer to the fixed local proceedings PDF.
