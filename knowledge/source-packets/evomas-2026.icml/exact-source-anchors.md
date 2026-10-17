# Exact source anchors

## Selected mechanism

We propose Evolutionary Generation of Multi-Agent Systems (EvoMAS), which formulates MAS generation as structured configuration generation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | system |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/prompts/render.py:8` | `render_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/registry.py:9` | `ToolRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/base.py:9` | `BaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/registry.py:10` | `PromptRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/topology/context.py:9` | `Context` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/spec.py:22` | `get_backend_for_agent_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/spec.py:34` | `AgentSpec` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/spec.py:55` | `AgentResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/workbench_stubs.py:16` | `email_send_email` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/workbench_stubs.py:31` | `email_delete_email` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/workbench_stubs.py:44` | `email_forward_email` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/workbench_tools_calendar.py:17` | `reset_state` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/workbench_tools_calendar.py:22` | `calendar_get_event_information_by_id` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/workbench_tools_calendar.py:47` | `calendar_search_events` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/meta_model/reward.py:15` | `compute_reward` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/meta_model/reward.py:67` | `compare_configurations` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/meta_model/reward.py:96` | `should_add_to_pool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/workbench_tools_email.py:21` | `reset_state` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `93fd9d6766b093f6bbdeeffc35896910cbece6e2`. Paper page numbers refer to the fixed local proceedings PDF.
