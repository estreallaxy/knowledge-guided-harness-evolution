# Exact source anchors

## Selected mechanism

To address these challenges, we introduce TRACE (Traversal Retrieval-Augmented Chain of Evidence).

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | method |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5 Experiments |
| Results and ablations | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | Analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/environment.py:19` | `BookEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents.py:22` | `AgenticSystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config.py:13` | `ModelConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config.py:22` | `Config` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace/run_agentic_rag_global.py:10` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace/run_agentic_rag_book.py:11` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace/agent_shared.py:25` | `ModelConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace/agent_shared.py:61` | `BookEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace/agent_shared.py:228` | `AgenticSystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace/run_agentic_rag.py:32` | `ModelConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace/run_agentic_rag.py:82` | `BookEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/trace/run_agentic_rag.py:211` | `search_pages_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/evaluate.py:10` | `evaluate_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/evaluate.py:90` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/run_chapter_mode.py:20` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/run_global_mode.py:20` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/run_book_mode.py:21` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/embed/statistic.py:7` | `analyze_data_stats` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `163c1ecb404f44e8428bb05e013bd9ce3cffb20f`. Paper page numbers refer to the fixed local proceedings PDF.
