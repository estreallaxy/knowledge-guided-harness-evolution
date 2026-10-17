# Exact source anchors

## Selected mechanism

Retain Mosaic's mask-only logits kernel, lazy chunking optimizer, global virtual-addressed memory manager, and dynamic peak-control policy; the inference system is training-free.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | architecture |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tests/tools/test_config_validator.py:46` | `test_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/validate_config.py:13` | `get_attr_docs` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/validate_config.py:61` | `ConfigValidator` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/validate_config.py:85` | `validate_class` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_scheduler_encoder_decoder.py:14` | `test_scheduler_schedule_simple_encoder_decoder` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_chunked_prefill_scheduler.py:18` | `get_sequence_groups` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_chunked_prefill_scheduler.py:22` | `append_new_token` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_chunked_prefill_scheduler.py:27` | `schedule_and_update_computed_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_scheduler.py:24` | `test_scheduler_add_seq_group` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_scheduler.py:47` | `test_scheduler_abort_seq_group` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_scheduler.py:74` | `test_scheduler_schedule_simple` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/v1/core/test_scheduler_e2e.py:17` | `llm` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/v1/core/test_scheduler_e2e.py:27` | `test_concurrent_partial_prefill` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/v1/core/test_scheduler_e2e.py:34` | `test_prefix_cache_stats_is_recorded` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/v1/core/test_async_scheduler.py:14` | `_make_model_runner_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/v1/core/test_async_scheduler.py:32` | `test_stop_by_max_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/v1/core/test_async_scheduler.py:58` | `test_abort` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/v1/core/test_single_type_kv_cache_manager.py:17` | `get_sliding_window_manager` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `4441da142ad20af73f16551ae4d77a3863377e7b`. Paper page numbers refer to the fixed local proceedings PDF.
