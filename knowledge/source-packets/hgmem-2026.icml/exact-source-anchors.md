# Exact source anchors

## Selected mechanism

We introduce HGMem, a hypergraph-based working memory system, extending the concept of memory beyond simple storage into a dynamic, expressive structure for complex reasoning and global understanding.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | system |
| Experimental setup | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | experiments |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluate/evaluate_by_scoring.py:123` | `post_process_evaluate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate/evaluate_by_scoring.py:152` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/build_graph.py:28` | `normalize_question_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/build_graph.py:35` | `rag_insert` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/manipulate_graph.py:14` | `build_new_entity_vdb_for_graph` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/manipulate_graph.py:38` | `build_new_relationship_vdb_for_graph` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/manipulate_graph.py:64` | `build_new_chunk_vdb_for_graph` | Pinned implementation entry for the selected mechanism. |
| `official-code/myrag/memory.py:14` | `postprocess_evolve_memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/myrag/memory.py:81` | `postprocess_summarize_absent_entities_relationships` | Pinned implementation entry for the selected mechanism. |
| `official-code/myrag/memory.py:136` | `postprocess_reorganize_memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/inspection.py:14` | `inspect_raised_questions` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/inspection.py:45` | `inspect_multiturn_reasoning` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/inspection.py:71` | `inspect_entity_distribution_across_chunks` | Pinned implementation entry for the selected mechanism. |
| `official-code/myrag/base.py:17` | `QueryParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/myrag/base.py:73` | `StorageNameSpace` | Pinned implementation entry for the selected mechanism. |
| `official-code/myrag/base.py:87` | `BaseVectorStorage` | Pinned implementation entry for the selected mechanism. |
| `official-code/myrag/storage.py:30` | `JsonKVStorage` | Pinned implementation entry for the selected mechanism. |
| `official-code/myrag/storage.py:71` | `NanoVectorDBStorage` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `1cd9ca4d7498ff7cbf1727957ff40d7e9c44942f`. Paper page numbers refer to the fixed local proceedings PDF.
