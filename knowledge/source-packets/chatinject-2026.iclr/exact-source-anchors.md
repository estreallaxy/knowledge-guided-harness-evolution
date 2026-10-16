# Exact source anchors

## Selected mechanism

Expose and test prompt-injection paths created by chat-template boundaries and agent message serialization.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | System |
| Experimental setup | PDF p.11; `paper/paper-iclr2026.txt` marker `===== PDF p.11 =====` | experiments |
| Results and ablations | PDF p.15; `paper/paper-iclr2026.txt` marker `===== PDF p.15 =====` | Analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agentdojo/functions_runtime.py:12` | `TaskEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/functions_runtime.py:18` | `EmptyEnv` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/functions_runtime.py:25` | `Depends` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/attack_registry.py:13` | `register_attack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/attack_registry.py:40` | `load_attack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/agent_pipeline/planner.py:8` | `ToolSelector` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/agent_pipeline/planner.py:28` | `ToolUsagePlanner` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/dos_attacks.py:10` | `DoSAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/dos_attacks.py:39` | `SwearwordsDoSAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/dos_attacks.py:57` | `CaptchaDoSAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/important_instructions_attacks.py:18` | `get_wrong_model_name_from_pipeline` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/important_instructions_attacks.py:26` | `ImportantInstructionsAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/important_instructions_attacks.py:47` | `ImportantInstructionsAttackNoUserName` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/base_attacks.py:25` | `BaseAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/base_attacks.py:99` | `FixedJailbreakAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/base_attacks.py:128` | `get_model_name_from_pipeline` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/agent_pipeline/tool_execution.py:14` | `is_string_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/agent_pipeline/tool_execution.py:22` | `tool_result_to_str` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c6832ab413ebb4728f7b18640702df542e8b4142`. Paper page numbers refer to the fixed local proceedings PDF.
