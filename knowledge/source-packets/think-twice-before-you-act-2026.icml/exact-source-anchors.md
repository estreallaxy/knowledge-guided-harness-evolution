# Exact source anchors

## Selected mechanism

Building on this insight, we propose Tool-Guard, a novel system-level defense based on a new concept called isolated planning , in which tool invocations that are detected as misaligned or suspicious cause the corresponding tool to be placed in a quarantined list (the influenced list ), breaking further influence from poisoned descriptions.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | system |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.3. Analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agentdojo/agent_pipeline/tool_description_defense.py:76` | `DefenseResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/agent_pipeline/tool_description_defense.py:87` | `ToolDescriptionDefenseStats` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/agent_pipeline/tool_description_defense.py:100` | `ToolDescriptionDefense` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/tool_description_poisoning.py:38` | `ToolDescriptionPoisoner` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/tool_description_poisoning.py:110` | `append_instruction_strategy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/tool_description_poisoning.py:134` | `prepend_instruction_strategy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/functions_runtime.py:12` | `TaskEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/functions_runtime.py:18` | `EmptyEnv` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/functions_runtime.py:25` | `Depends` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/attack_registry.py:13` | `register_attack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/attack_registry.py:40` | `load_attack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/agent_pipeline/planner.py:8` | `ToolSelector` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/agent_pipeline/planner.py:28` | `ToolUsagePlanner` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/baseline_attacks.py:10` | `ManualAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/baseline_attacks.py:28` | `DirectAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/baseline_attacks.py:42` | `IgnorePreviousAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/dos_attacks.py:10` | `DoSAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agentdojo/attacks/dos_attacks.py:39` | `SwearwordsDoSAttack` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b70f711d8710251a7c2503eff6582aff7d731eff`. Paper page numbers refer to the fixed local proceedings PDF.
