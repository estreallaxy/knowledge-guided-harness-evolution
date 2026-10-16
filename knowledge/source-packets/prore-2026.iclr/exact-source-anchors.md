# Exact source anchors

## Selected mechanism

Have a reasoner schedule targeted state probes and evaluator actors collect fresh evidence before assigning a reward.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | system |
| Results and ablations | PDF p.18; `paper/paper-iclr2026.txt` marker `===== PDF p.18 =====` | Analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/android_world/agents/general_evaluator.py:348` | `load_gt_dataframe` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/general_evaluator.py:383` | `load_gt_from_traj` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/general_evaluator.py:400` | `compare_with_gt` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/evaluator.py:51` | `ProRe` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/evaluator.py:896` | `pretty_ui_snapshot` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/evaluator.py:936` | `extract_step_information` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/reward_model.py:19` | `load_dpo_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/reward_model.py:65` | `load_dpo_model_v2` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/reward_model.py:108` | `load_lora_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt_template.py:191` | `action_completion_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt_template.py:220` | `summarize_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt_template.py:248` | `action_selection_prompt_with_verifier` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/agent_utils.py:22` | `extract_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/base_agent.py:26` | `AgentInteractionResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/base_agent.py:39` | `EnvironmentInteractingAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/m3a_utils.py:26` | `_logical_to_physical` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/m3a_utils.py:63` | `_ui_element_logical_corner` | Pinned implementation entry for the selected mechanism. |
| `official-code/android_world/agents/m3a_utils.py:114` | `add_ui_element_mark` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `67cdbea86102235de901e98efbd0d641241cf925`. Paper page numbers refer to the fixed local proceedings PDF.
