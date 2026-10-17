# Exact source anchors

## Selected mechanism

We present GameDevBench, the first benchmark for evaluating agents on game development tasks.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 80 analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/gamedevbench/src/utils/prompts.py:13` | `load_task_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/utils/prompts.py:27` | `create_task_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/utils/prompts.py:90` | `create_system_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/benchmark_runner.py:48` | `_run_task_worker` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/benchmark_runner.py:71` | `GodotBenchmarkRunner` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/benchmark_runner.py:1905` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/utils/validation.py:13` | `ValidationParser` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/utils/merge_benchmark_results.py:15` | `_load_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/utils/merge_benchmark_results.py:19` | `_task_map` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/utils/merge_benchmark_results.py:29` | `_selected_tasks` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_prompts.py:4` | `test_task_prompt_ends_with_filesystem_and_documentation_scope` | Pinned implementation entry for the selected mechanism. |
| `official-code/validate_tasks.py:46` | `validate_one` | Pinned implementation entry for the selected mechanism. |
| `official-code/validate_tasks.py:73` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_merge_benchmark_results.py:6` | `test_merge_results_replaces_exact_manifest_and_recomputes_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_benchmark_resume.py:6` | `test_results_resume_only_redoes_selected_incomplete_tasks` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_benchmark_resume.py:50` | `test_task_list_is_passed_as_resume_scope` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/virtual_display.py:12` | `VirtualDisplayError` | Pinned implementation entry for the selected mechanism. |
| `official-code/gamedevbench/src/virtual_display.py:16` | `needs_virtual_display` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `39952ba6341898380ff1c2c3336101c57c99196b`. Paper page numbers refer to the fixed local proceedings PDF.
