# Exact source anchors

## Selected mechanism

To exploit this vulnerability, we propose LogicPoison, a novel attack framework that targets logical reasoning rather than injecting false contents.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | Method |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5.2 Main Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src_plus/query_centric_retrieval.py:28` | `get_nlp` | Pinned implementation entry for the selected mechanism. |
| `official-code/src_plus/query_centric_retrieval.py:40` | `normalize_space` | Pinned implementation entry for the selected mechanism. |
| `official-code/src_plus/query_centric_retrieval.py:44` | `tokenize` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluator.py:24` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluator.py:50` | `exact_match` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluator.py:67` | `substring_match` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluator_llm.py:49` | `load_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluator_llm.py:65` | `save_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/evaluator_llm.py:79` | `get_cache_key` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:12` | `list_datasets` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:22` | `pick_stages` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:29` | `pick_datasets` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/global_poison.py:19` | `corpus_stats` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/global_poison.py:57` | `save_stats` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/global_poison.py:69` | `run_corpus` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/query_centric.py:16` | `_load_api_key` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/query_centric.py:23` | `_load_base_url` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/query_centric.py:31` | `make_prompt` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `293b327590d1d043065c3314ad787efb87c41d81`. Paper page numbers refer to the fixed local proceedings PDF.
