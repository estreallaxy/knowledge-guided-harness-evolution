# Exact source anchors

## Selected mechanism

Optimize modular system-prompt components with an edit-based genetic search and task-level evaluation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | system |
| Experimental setup | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | 1 Experiments |
| Results and ablations | PDF p.19; `paper/paper-iclr2026.txt` marker `===== PDF p.19 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/scripts/lib/eval/compute_metrics.py:45` | `average_token_count` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/compute_metrics.py:66` | `get_data_items` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/compute_metrics.py:75` | `pass_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/truthfulqa/metrics.py:15` | `run_end2end_GPT3` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/ds1000/score_analyzer.py:11` | `load_record` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/ds1000/score_analyzer.py:45` | `get_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/ds1000/cache_input_ans.py:12` | `cache_helper` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/ds1000/cache_input_ans.py:33` | `cache_input_ans` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/reward_modeling/main_multi_metric.py:68` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/reward_modeling/main_multi_metric.py:73` | `load_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/reward_modeling/main_multi_metric.py:79` | `build_pairs` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/reward_modeling/main_multi_metric_one.py:65` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/reward_modeling/main_multi_metric_one.py:70` | `load_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/reward_modeling/main_multi_metric_one.py:76` | `build_pairs` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/ifeval/instructions_util_test.py:23` | `InstructionsUtilTest` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/ifeval/instructions_test.py:24` | `InstructionsTest` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/ds1000/run_test.py:21` | `test_helper` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/lib/eval/ds1000/run_test.py:29` | `test_model` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `90e070ab40e9c76e5523d6840efa41a827c2bae8`. Paper page numbers refer to the fixed local proceedings PDF.
