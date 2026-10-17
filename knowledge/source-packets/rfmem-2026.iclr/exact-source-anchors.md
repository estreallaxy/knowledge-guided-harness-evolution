# Exact source anchors

## Selected mechanism

Retrieve personalized memories through a familiarity-first gate followed by selective recollection and evidence fusion.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | system |
| Results and ablations | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | results |
| Limitations or failure conditions | PDF p.36; `paper/paper-iclr2026.txt` marker `===== PDF p.36 =====` | Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/RF_mem/LongMemEval/src/retrieval/eval_utils.py:4` | `dcg` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/retrieval/eval_utils.py:12` | `ndcg` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/retrieval/eval_utils.py:24` | `evaluate_retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/retrieval/index_expansion_utils.py:4` | `fetch_expansion_from_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/retrieval/index_expansion_utils.py:17` | `resolve_expansion` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/evaluation/evaluate_qa.py:20` | `chat_completions_with_backoff` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/evaluation/evaluate_qa.py:24` | `get_anscheck_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/index_expansion/temp_query_search_pruning.py:12` | `increment_date` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/index_expansion/temp_query_search_pruning.py:25` | `chat_completions_with_backoff` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/index_expansion/temp_query_search_pruning.py:39` | `infer_time_range` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/retrieval/RF_mem.py:39` | `safe_generate` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/retrieval/RF_mem.py:49` | `_entropy_from_scores` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/retrieval/RF_mem.py:58` | `decide_strategy_with_probe` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/index_expansion/batch_expansion_session_keyphrases.py:10` | `chat_completions_with_backoff` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/index_expansion/batch_expansion_session_keyphrases.py:20` | `generate_session_keyphrases` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/index_expansion/batch_expansion_turn_keyphrases.py:10` | `chat_completions_with_backoff` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/index_expansion/batch_expansion_turn_keyphrases.py:19` | `generate_round_keyphrases` | Pinned implementation entry for the selected mechanism. |
| `official-code/RF_mem/LongMemEval/src/index_expansion/batch_expansion_session_summ.py:10` | `chat_completions_with_backoff` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d6a2cb3416e8320bcb1439921d319729aeccec8e`. Paper page numbers refer to the fixed local proceedings PDF.
