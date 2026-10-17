# Exact source anchors

## Selected mechanism

Retain the capacity-bounded external experience library and the failure-driven textual Add, Edit, and Delete operations with dual verification; textual gradients modify external memory, not model parameters.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | framework |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 5. Experiments |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agents/evaluator.py:7` | `calculate_pass_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/evaluator.py:27` | `EvaluatorAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/retriever.py:15` | `RetrievalAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/retriever.py:416` | `calculate_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/retriever.py:431` | `evaluate_retriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/quick_query.py:11` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/base_agent.py:5` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/generate_index.py:14` | `load_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/generate_index.py:31` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/optimizer.py:12` | `OptimizerAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/solver.py:9` | `SolverAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/initializer.py:19` | `InitAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/initializer.py:161` | `generate_embeddings` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/initializer.py:248` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/grader.py:19` | `choice_answer_clean` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/grader.py:32` | `parse_digits` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/grader.py:54` | `is_digit` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/utils.py:29` | `DatasetType` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `bf7b467d2151e3d26d3543ba01322fd29c8f518f`. Paper page numbers refer to the fixed local proceedings PDF.
