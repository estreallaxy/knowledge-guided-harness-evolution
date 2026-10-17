# Exact source anchors

## Selected mechanism

Evaluate long-term memory over coherent million-token histories and use external episodic, working, and scratchpad memory.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | system |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/evaluation/compute_metrics.py:21` | `get_or_create_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/compute_metrics.py:29` | `initialize_models` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/compute_metrics.py:49` | `compute_bleu` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/answer_probing_questions/long_term_memory_methods.py:41` | `_get_st_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/answer_probing_questions/long_term_memory_methods.py:60` | `safe_encode` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/answer_probing_questions/long_term_memory_methods.py:68` | `hf_emb_from_cached_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/report_results.py:7` | `report_llms_accuracies` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/run_evaluation.py:12` | `get_rubric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/run_evaluation.py:22` | `run_evaluation` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/run_evaluation.py:90` | `run_evaluation_event_ordering` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/llm.py:6` | `BuildLLm` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/beam/adjust_chats_length.py:10` | `chats_tokens_counter` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/beam/adjust_chats_length.py:36` | `count_message_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/beam/adjust_chats_length.py:67` | `count_chats_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/beam/download_dataset.py:11` | `convert_user_messages_pickle_to_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/beam/download_dataset.py:37` | `convert_chats_pickle_to_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/beam/download_dataset.py:67` | `fix_10m_chats` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/beam/run_pipeline.py:13` | `run_plans_generation` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b2da22eac88bb0874c64665f13457eb99835774a`. Paper page numbers refer to the fixed local proceedings PDF.
