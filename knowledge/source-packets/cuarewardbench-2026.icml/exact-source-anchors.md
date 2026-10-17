# Exact source anchors

## Selected mechanism

To address this gap, we present CUARewardBench, comprising four key contributions: (1) First-ever Comprehensive CUA Reward Benchmark: We introduce the first benchmark for evaluating both outcome reward models (ORM) and process reward models (PRM) on CUA tasks, enabling systematic assessment across trajectory-level and step-level evaluation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | framework |
| Experimental setup | PDF p.17; `paper/paper-icml2026.txt` marker `===== PDF p.17 =====` | Experimental Setup |
| Results and ablations | PDF p.17; `paper/paper-icml2026.txt` marker `===== PDF p.17 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/cuarewardbench/core/metrics_calculator.py:14` | `compute_binary_classification_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/metrics_calculator.py:53` | `analyze_group_performance` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/metrics_calculator.py:101` | `update_group_stats` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/model_config.py:12` | `_optional_env` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/model_config.py:20` | `_openai_compatible_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/config.py:21` | `_discover_model_configs` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/config.py:56` | `available_eval_modes` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/config.py:60` | `validate_eval_mode` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/llm_eval.py:31` | `LLMEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/cli/eval_trajectory.py:74` | `scan_trajectory_dirs` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/cli/eval_trajectory.py:198` | `prepare_trajectory_from_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/cli/eval_trajectory.py:265` | `evaluate_single_trajectory` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/data_io.py:8` | `_find_osworld_examples_root` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/data_io.py:25` | `get_instruction` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/core/data_io.py:46` | `load_data_items` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/cli/eval_benchmark.py:78` | `evaluate_cuarewardbench` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/cli/eval_benchmark.py:115` | `process_single_task_wrapper` | Pinned implementation entry for the selected mechanism. |
| `official-code/cuarewardbench/cli/eval_benchmark.py:164` | `process_tasks` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `33a04c96b86cea643f9d396e4879f778717fb923`. Paper page numbers refer to the fixed local proceedings PDF.
