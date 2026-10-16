# Exact source anchors

## Selected mechanism

Use an Evolver LLM to revise prompts, memory, hyperparameters, and tool routines from each episode transcript without gradients.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | system |
| Experimental setup | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | Experiments |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/memory_agent.py:3` | `MemoryAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_naive_agent.py:13` | `test_naive_agent_initialization` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_naive_agent.py:35` | `test_memory_methods` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_naive_agent.py:58` | `test_episode_management` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_rag_agent.py:14` | `MockArgs` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_rag_agent.py:26` | `MockStateNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_rag_agent.py:31` | `test_rag_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_rag_agent_embeddings.py:14` | `test_rag_agent_initialization` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_rag_agent_embeddings.py:50` | `test_history_management` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_rag_agent_embeddings.py:86` | `test_entity_extraction` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cross_episode_memory.py:7` | `CrossEpisodeMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/naive_agent.py:3` | `NaiveAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/summary_agent.py:3` | `SummaryAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/rag_agent.py:6` | `RAGAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/our_agent.py:6` | `OurAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation.py:16` | `StateNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation.py:22` | `GameEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/console_play.py:5` | `main` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `f92474ce83c7aec69e45c30ccfaf2b69e66823de`. Paper page numbers refer to the fixed local proceedings PDF.
