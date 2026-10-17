# Exact source anchors

## Selected mechanism

To bridge this gap, we introduce DeepCommit, an agentic pipeline that reconstructs verifiable Milestone DAGs from noisy commit logs, where milestones are defined as functionally cohesive development goals.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.15; `paper/paper-icml2026.txt` marker `===== PDF p.15 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | system |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/harness/test_runner/core/test_executor.py:47` | `extract_first_fatal_error` | Pinned implementation entry for the selected mechanism. |
| `official-code/harness/test_runner/core/test_executor.py:73` | `get_default_test_cmd` | Pinned implementation entry for the selected mechanism. |
| `official-code/harness/test_runner/core/test_executor.py:105` | `build_test_cmd` | Pinned implementation entry for the selected mechanism. |
| `official-code/harness/test_runner/core/docker.py:18` | `check_image_exists` | Pinned implementation entry for the selected mechanism. |
| `official-code/harness/test_runner/core/docker.py:32` | `build_docker_image` | Pinned implementation entry for the selected mechanism. |
| `official-code/harness/test_runner/core/docker.py:70` | `cleanup_docker_image` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_agent_prompt.py:4` | `test_submission_command_uses_shell_paths_and_root_manifests` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_tool_search_setting.py:25` | `test_validate_tool_search_setting_accepts_native_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_tool_search_setting.py:29` | `test_validate_tool_search_setting_passes_none_through` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_tool_search_setting.py:37` | `test_validate_tool_search_setting_rejects_invalid_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_evaluator_compile_fail_closed.py:9` | `_evaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_evaluator_compile_fail_closed.py:34` | `test_compile_failure_on_both_bases_fails_closed` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_evaluator_compile_fail_closed.py:51` | `test_start_fallback_can_succeed_after_end_compile_failure` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_evaluator_filter.py:8` | `_empty_failed_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_evaluator_filter.py:31` | `test_zero_test_result_cannot_become_resolved_or_negative` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_evaluator_filter.py:50` | `test_invalid_p2p_count_cannot_drive_required_below_zero` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_rescore_filter_only.py:32` | `_world` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/e2e/test_rescore_filter_only.py:36` | `_fo` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `17a8f1593e172e26b36cea15e2b30fb9536c93f5`. Paper page numbers refer to the fixed local proceedings PDF.
