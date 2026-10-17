# Exact source anchors

## Selected mechanism

To explore this, we introduce AI-Work, a tractable, simulated gig economy where Large Language Model (LLM) agents compete for jobs, develop skills, and adapt their strategies under uncertainty and competitive pressure.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | Design |
| Experimental setup | PDF p.23; `paper/paper-icml2026.txt` marker `===== PDF p.23 =====` | experiments |
| Results and ablations | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | Results |
| Limitations or failure conditions | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 5. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/ssa/agents/policy.py:22` | `PolicyAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/ssa_agent.py:83` | `SSAAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/oracle.py:86` | `OracleAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/ssa_agent_ablation.py:88` | `SSAAgentAblation` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/react_agent.py:75` | `ReActAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/react_agent.py:285` | `test_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/cot_agent.py:83` | `CoTAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/cot_agent.py:289` | `test_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/agent.py:26` | `AgentBase` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/agent.py:217` | `plot_agent_history` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/agents/agent.py:228` | `StaticAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/agents.py:22` | `test_oracle_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/experiment_config.py:8` | `deep_merge` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/experiment_config.py:20` | `ModelSpec` | Pinned implementation entry for the selected mechanism. |
| `official-code/ssa/experiment_config.py:31` | `TaskSpec` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_seeding.py:8` | `test_set_seed_deterministic` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_payments.py:4` | `test_adjusted_reward_with_performance_pay` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_payments.py:8` | `test_adjusted_reward_without_performance_pay` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `293c17e6afe992c1ac4f1a90b9f2d7e15f9f23d8`. Paper page numbers refer to the fixed local proceedings PDF.
