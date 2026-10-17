# Exact source anchors

## Selected mechanism

We introduce a reproducible simulation framework to evaluate generative agents in three aspects: (1) safety improvement over time via iterative plan revision in multimodal scenarios; (2) detection of unsafe activities across social contexts; and (3) social dynamics, measured through interaction and acceptance rates.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | ablation |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/reverie/backend_server/persona/prompt_template/v2/memory_retrieval_v1_cot.py:11` | `create_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/memory_retrieval_v1_cot.py:66` | `MemoryRelevance` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/memory_retrieval_v1_cot.py:72` | `run_gpt_prompt_memory_retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/frontend_server/translator/migrations/0002_evaldata_target_agent.py:6` | `Migration` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/safety/anthromorphosization_v1.py:10` | `create_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/safety/anthromorphosization_v1.py:21` | `SafetyScore` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/safety/anthromorphosization_v1.py:26` | `run_gpt_generate_safety_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/planning_thought_on_convo_v1.py:11` | `create_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/planning_thought_on_convo_v1.py:26` | `PlanningThought` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/planning_thought_on_convo_v1.py:30` | `run_gpt_prompt_planning_thought_on_convo` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/planning_thought_on_convo_v2_cot.py:11` | `create_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/planning_thought_on_convo_v2_cot.py:70` | `PlanningThought` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/planning_thought_on_convo_v2_cot.py:75` | `run_gpt_prompt_planning_thought_on_convo` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/new_decomp_schedule_v1.py:12` | `create_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/new_decomp_schedule_v1.py:36` | `NewActivity` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/new_decomp_schedule_v1.py:43` | `NewSchedule` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/generate_hourly_schedule_v2.py:11` | `create_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/reverie/backend_server/persona/prompt_template/v2/generate_hourly_schedule_v2.py:37` | `Activity` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `65cc83d77b6df096a81d0dd6f3d555000702497f`. Paper page numbers refer to the fixed local proceedings PDF.
