# Exact source anchors

## Selected mechanism

Consolidate memories at multiple granularities, route retrieval by entropy, and filter the retrieved evidence.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Method |
| Experimental setup | PDF p.29; `paper/paper-iclr2026.txt` marker `===== PDF p.29 =====` | Experimental Setup |
| Results and ablations | PDF p.29; `paper/paper-iclr2026.txt` marker `===== PDF p.29 =====` | Results |
| Limitations or failure conditions | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | limitation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/retrieval/eval_utils.py:4` | `dcg` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retrieval/eval_utils.py:12` | `ndcg` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retrieval/eval_utils.py:24` | `evaluate_retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/generation/metrics.py:15` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/generation/metrics.py:34` | `normalize_zh_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/generation/metrics.py:51` | `count_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retrieval/run_retrieval.py:21` | `run_ppr` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retrieval/run_retrieval.py:34` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retrieval/run_retrieval.py:50` | `multi_granularity_routing` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/llm_judge_single.py:47` | `calculate_single` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/eval_query_type.py:13` | `get_qa_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/eval_query_type.py:50` | `calculate_single` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/eval_query_type.py:66` | `print_type_metric` | Pinned implementation entry for the selected mechanism. |
| `official-code/quickstart/memory.py:17` | `MemGASMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/quickstart/retriever.py:15` | `MultiGranRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/quickstart/config.py:22` | `MemoryConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/generation/async_llm.py:6` | `create_completion` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/generation/async_llm.py:40` | `run_async` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c2d4e9fdc331074802a711baf4371197f9194399`. Paper page numbers refer to the fixed local proceedings PDF.
