# Exact source anchors

## Selected mechanism

Based on this conclusion, we propose HiCBench, which includes manually annotated multi-level document chunking points, synthesized evidence-dense question answer(QA) pairs, and their corresponding evidence sources.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | approach |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | results |
| Limitations or failure conditions | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/metrics.py:31` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:59` | `normalize_zh_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:82` | `bleu_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/retrieval_algo.py:17` | `tree_chunk_retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/retrieval_algo.py:50` | `check_merge_condition` | Pinned implementation entry for the selected mechanism. |
| `official-code/retrieval_algo.py:118` | `remove_repeat_passages` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:41` | `scorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/retrieval/passage_retrieval.py:13` | `Indexer` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/retrieval/passage_retrieval.py:101` | `load_passages` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/retrieval/passage_retrieval.py:112` | `embed_queries` | Pinned implementation entry for the selected mechanism. |
| `official-code/cov_mertic.py:72` | `call_api` | Pinned implementation entry for the selected mechanism. |
| `official-code/cov_mertic.py:97` | `compute_coverage_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/cov_mertic.py:133` | `_extract_facts` | Pinned implementation entry for the selected mechanism. |
| `official-code/pred.py:21` | `call_vllm` | Pinned implementation entry for the selected mechanism. |
| `official-code/pred.py:47` | `load_passages` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `8d17d18931123bb4ea7b06cd394e4336085c7471`. Paper page numbers refer to the fixed local proceedings PDF.
