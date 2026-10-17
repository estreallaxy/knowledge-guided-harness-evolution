# Exact source anchors

## Selected mechanism

Retain the dynamic non-parametric trajectory memory, on-the-fly advantage estimation, and inference-time logit modulation; the selected mechanism performs no gradient update or parameter training.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Method |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 5. Experiments |
| Results and ablations | PDF p.18; `paper/paper-icml2026.txt` marker `===== PDF p.18 =====` | ANALYSIS |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/WebArena/memory_agents/dynamic_prompting.py:29` | `Flags` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/memory_agents/dynamic_prompting.py:76` | `PromptElement` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/memory_agents/dynamic_prompting.py:147` | `Shrinkable` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/memory_agents/utils/prompt_templates.py:13` | `PromptTemplate` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/memory_agents/utils/prompt_templates.py:66` | `get_prompt_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/autoeval/evaluate_trajectory.py:21` | `extract_think_and_action` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/autoeval/evaluate_trajectory.py:26` | `extract_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/autoeval/evaluate_trajectory.py:50` | `process_sample` | Pinned implementation entry for the selected mechanism. |
| `official-code/Jericho/src/naive_agent.py:3` | `NaiveAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/Jericho/src/awm_agent.py:6` | `AWMAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/Jericho/src/prompt_update_with_history.py:11` | `load_episodes_history` | Pinned implementation entry for the selected mechanism. |
| `official-code/Jericho/src/prompt_update_with_history.py:22` | `get_top_episodes` | Pinned implementation entry for the selected mechanism. |
| `official-code/Jericho/src/prompt_update_with_history.py:29` | `extract_episode_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/Jericho/src/cross_episode_memory.py:17` | `CrossEpisodeMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/Jericho/src/jitrl_agent.py:9` | `JitRLAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/memory_agents/jitrl_agent.py:20` | `StateNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/memory_agents/jitrl_agent.py:29` | `JitRLAgentArgs` | Pinned implementation entry for the selected mechanism. |
| `official-code/WebArena/memory_agents/jitrl_agent.py:43` | `BrowserGymJitRLAgent` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `143d22185d95fbf633a0befe6861d5e8b732543b`. Paper page numbers refer to the fixed local proceedings PDF.
