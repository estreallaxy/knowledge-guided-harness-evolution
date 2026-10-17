# Exact source anchors

## Selected mechanism

To address this issue, we propose CheckRLM , a framework that improves the reliability of the reasoning process through Retrieval-Augmented Generation (RAG) by timely checking and correcting factual errors.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.14; `paper/paper-acl2026.txt` marker `===== PDF p.14 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | approach |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4 Experiments |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5 Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/evaluate.py:7` | `acc_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate.py:24` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate.py:42` | `compute_exact` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retrieve.py:4` | `retrieve_single_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retrieve.py:29` | `get_retrieved_docs` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/bm25_retriever.py:15` | `ElasticSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/bm25_retriever.py:100` | `retrieve_single_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils.py:11` | `safe_api_call` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils.py:14` | `load_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils.py:20` | `load_yaml` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/build_index/preprocess_datasets.py:20` | `hash_object` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/build_index/preprocess_datasets.py:28` | `process_line` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/build_index/preprocess_datasets.py:49` | `generate_indexing_docs_from_bz2` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tasks/base.py:27` | `parse_arguments` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tasks/base.py:114` | `generate_single_step` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tasks/base.py:173` | `process_single_sample` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tasks/check_think_offline.py:30` | `parse_arguments` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tasks/check_think_offline.py:122` | `generate_single_step` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `44ed3dc4090fb472e5a11c81cf0dbd15e4ef268c`. Paper page numbers refer to the fixed local proceedings PDF.
