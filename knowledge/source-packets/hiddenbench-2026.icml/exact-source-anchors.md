# Exact source anchors

## Selected mechanism

We introduce HiddenBench, a 65-task benchmark grounded in the Hidden Profile paradigm, which isolates collective reasoning under distributed information from individual reasoning ability.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.12; `paper/paper-icml2026.txt` marker `===== PDF p.12 =====` | framework |
| Experimental setup | PDF p.13; `paper/paper-icml2026.txt` marker `===== PDF p.13 =====` | experiments |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 6. Ablation |
| Limitations or failure conditions | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/hiddenbench/metrics.py:11` | `load_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/metrics.py:16` | `_sem` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/metrics.py:22` | `_task_lookup` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_metrics.py:7` | `test_score_results_average_and_majority` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_metrics.py:37` | `test_score_legacy_conditions_schema` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/prompts.py:8` | `PromptSet` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/prompts.py:27` | `default_prompt_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/prompts.py:35` | `load_prompts` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/benchmark.py:14` | `BenchmarkTask` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/benchmark.py:64` | `validate_task_mapping` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/benchmark.py:96` | `validate_benchmark` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_benchmark.py:8` | `test_load_short_benchmark` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_benchmark.py:16` | `test_rejects_invalid_correct_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/generation.py:39` | `ValidationResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/generation.py:57` | `generate_task` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/generation.py:67` | `validate_task_candidate` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/models.py:14` | `ModelClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/hiddenbench/models.py:26` | `extract_json_object` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3be6ca16973e4fb751ffc0dfb7eb11f2d28335d1`. Paper page numbers refer to the fixed local proceedings PDF.
