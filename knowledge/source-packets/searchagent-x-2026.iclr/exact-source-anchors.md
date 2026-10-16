# Exact source anchors

## Selected mechanism

Allocate search, reading, and reasoning effort according to observed marginal utility and stop unproductive branches early.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | approach |
| Experimental setup | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Experiments |
| Results and ablations | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | results |
| Limitations or failure conditions | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tests/core/test_scheduler.py:13` | `get_sequence_groups` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_scheduler.py:17` | `test_scheduler_add_seq_group` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/test_scheduler.py:33` | `test_scheduler_abort_seq_group` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/metrics/test_metrics.py:11` | `test_metric_counter_prompt_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/metrics/test_metrics.py:44` | `test_metric_counter_generation_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/spec_decode/test_metrics.py:10` | `test_initial_call_returns_none` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/spec_decode/test_metrics.py:28` | `test_second_call_returns_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/spec_decode/test_metrics.py:56` | `test_nonzero_rank_noop` | Pinned implementation entry for the selected mechanism. |
| `official-code/setup.py:26` | `is_sccache_available` | Pinned implementation entry for the selected mechanism. |
| `official-code/setup.py:30` | `is_ccache_available` | Pinned implementation entry for the selected mechanism. |
| `official-code/setup.py:34` | `is_ninja_available` | Pinned implementation entry for the selected mechanism. |
| `official-code/vllm/core/scheduler.py:18` | `PreemptionMode` | Pinned implementation entry for the selected mechanism. |
| `official-code/vllm/core/scheduler.py:35` | `ScheduledSequenceGroup` | Pinned implementation entry for the selected mechanism. |
| `official-code/vllm/core/scheduler.py:46` | `SchedulerOutputs` | Pinned implementation entry for the selected mechanism. |
| `official-code/vllm/entrypoints/searchagent-x.py:55` | `LLM` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/utils.py:8` | `create_dummy_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/utils.py:26` | `create_seq_group` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/core/utils.py:63` | `round_up_to_next_block` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `5faabdb76a8e36eceb0c4f6441870d7f4285fa17`. Paper page numbers refer to the fixed local proceedings PDF.
