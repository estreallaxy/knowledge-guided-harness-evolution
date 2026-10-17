# Exact source anchors

## Selected mechanism

To this end, we propose LegalGraphRAG, a framework designed for reliable legal reasoning.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | approach |
| Experimental setup | PDF p.18; `paper/paper-acl2026.txt` marker `===== PDF p.18 =====` | experiments |
| Limitations or failure conditions | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | 3.3 Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/core/LegalGraphRAG.py:16` | `ModelConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/LegalGraphRAG.py:48` | `DataConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/LegalGraphRAG.py:61` | `RetrieveConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/prompt/__init__.py:103` | `set_prompt_language` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/prompt/__init__.py:112` | `get_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/graph_construct/graph_db.py:10` | `InMemoryGraphDB` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/graph_construct/graph_db.py:243` | `GraphDBManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/graph_construct/feature_graph.py:12` | `configure_embedding` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/graph_construct/feature_graph.py:21` | `get_embedding` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/graph_construct/feature_graph.py:40` | `summarize_texts` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/merge_retrieval_corpus.py:18` | `load_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/merge_retrieval_corpus.py:26` | `normalized_fact` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/merge_retrieval_corpus.py:30` | `canonical_record` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/evaluate_results.py:49` | `load_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/evaluate_results.py:54` | `as_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/evaluate_results.py:62` | `normalize_charge` | Pinned implementation entry for the selected mechanism. |
| `official-code/run.py:12` | `load_test_cases` | Pinned implementation entry for the selected mechanism. |
| `official-code/run.py:24` | `process_cases_worker` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a3c9c3070cadb72ec317d2ecc2cce99da4b37c57`. Paper page numbers refer to the fixed local proceedings PDF.
