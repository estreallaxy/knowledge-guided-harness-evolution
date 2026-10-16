# Exact source anchors

## Selected mechanism

Detect and rectify misinformation in multi-agent information flows with goal-aware, training-free reasoning.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.14; `paper/paper-iclr2026.txt` marker `===== PDF p.14 =====` | architecture |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | analysis |
| Limitations or failure conditions | PDF p.24; `paper/paper-iclr2026.txt` marker `===== PDF p.24 =====` | discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run.py:6` | `run` | Pinned implementation entry for the selected mechanism. |
| `official-code/calculate.py:4` | `calculate_average_from_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/tool.py:4` | `call_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/tool.py:30` | `call_hijack_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/agent.py:34` | `Agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/agent.py:504` | `PlanningAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/agent.py:619` | `ConclusionAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/message.py:2` | `AgentMessage` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/action.py:1` | `Action` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/generate.py:3` | `generate_with_gpt` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/generate.py:25` | `agenerate` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/log.py:4` | `Log` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/log.py:48` | `PlanningLog` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/log.py:79` | `ConclusionLog` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/pre_info.py:1` | `preinstall_system_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/pre_info.py:21` | `preinstall_plan_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/pre_info.py:47` | `preinstall_self_plan_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/sandbox/edge_finder.py:10` | `normalize_scores_new` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9a5a6cb017dfc07e73c6f7ca398589fe021916e8`. Paper page numbers refer to the fixed local proceedings PDF.
