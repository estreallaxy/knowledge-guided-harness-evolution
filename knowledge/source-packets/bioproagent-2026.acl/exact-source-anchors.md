# Exact source anchors

## Selected mechanism

To address this, we propose BioProAgent , a neuro-symbolic framework that anchors probabilistic planning in a deterministic Finite State Machine (FSM).

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.23; `paper/paper-acl2026.txt` marker `===== PDF p.23 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4 Experiments |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4.2 Main Results |
| Limitations or failure conditions | PDF p.13; `paper/paper-acl2026.txt` marker `===== PDF p.13 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/prompts/planner.py:13` | `_phi_project_working_memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/planner.py:26` | `_summarize_tau` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/planner.py:38` | `build_planner_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/main_evaluate.py:30` | `ExecutionStatus` | Pinned implementation entry for the selected mechanism. |
| `official-code/main_evaluate.py:39` | `SessionState` | Pinned implementation entry for the selected mechanism. |
| `official-code/main_evaluate.py:63` | `ProAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/capabilities/retrieval/knowledge_sources.py:13` | `RetrievalResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/capabilities/retrieval/knowledge_sources.py:18` | `ExampleRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/capabilities/retrieval/knowledge_sources.py:29` | `CustomFaissRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/prompts.py:106` | `build_alignment_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/prompts.py:132` | `build_paint_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/baselines/base_agent.py:15` | `AgentResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/baselines/base_agent.py:36` | `StepRecord` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/baselines/base_agent.py:48` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/baselines/react_agent.py:13` | `ReActAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/planner_transfer_matrix.py:25` | `AgentState` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/planner_transfer_matrix.py:38` | `CognitivePhase` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/core/planner_transfer_matrix.py:47` | `ExecutionRecord` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `e18586ab4a2a851433bedc0e6940b77470355fd6`. Paper page numbers refer to the fixed local proceedings PDF.
