# Exact source anchors

## Selected mechanism

Use multi-agent debate over alternative symbolic translations and solver feedback to improve logical reasoning.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Method |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | ablation |
| Limitations or failure conditions | PDF p.26; `paper/paper-iclr2026.txt` marker `===== PDF p.26 =====` | Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agentverse/environments/llm_eval.py:6` | `LLMEvalEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/memory/base.py:9` | `BaseMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/memory/chat_history.py:12` | `ChatHistoryMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/agents/llm_eval_multi_agent.py:10` | `LLMEvalAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/base.py:15` | `BaseEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/basic.py:16` | `BasicEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/rules/base.py:20` | `Rule` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/rules/visibility/base.py:12` | `BaseVisibility` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/rules/order/base.py:12` | `BaseOrder` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/rules/visibility/all.py:13` | `AllVisibility` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/rules/updater/basic.py:6` | `BasicUpdater` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/rules/order/concurrent.py:13` | `ConcurrentOrder` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/rules/updater/base.py:17` | `BaseUpdater` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/environments/rules/describer/basic.py:13` | `BasicDescriber` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/agents/final_debate_multi_agent.py:6` | `FinalDebateMultiAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/agents/base.py:10` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/agents/plan_and_solve_agent.py:6` | `PlanAndSolveAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentverse/agents/llm_solver_agent.py:9` | `SolverResult` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `99e2a8387fec1ef7d48e28110c13fdbb85957550`. Paper page numbers refer to the fixed local proceedings PDF.
