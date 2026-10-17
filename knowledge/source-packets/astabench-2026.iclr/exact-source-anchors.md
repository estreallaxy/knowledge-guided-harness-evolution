# Exact source anchors

## Selected mechanism

Evaluate scientific agents through reproducible task suites, modular baselines, graders, and execution records.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.49; `paper/paper-iclr2026.txt` marker `===== PDF p.49 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.17; `paper/paper-iclr2026.txt` marker `===== PDF p.17 =====` | system |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Analysis |
| Limitations or failure conditions | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tests/tools/test_search.py:15` | `test_paper_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_search.py:35` | `test_snippet_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_search.py:55` | `test_paper_search_inserted_before` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_state_util.py:18` | `mock_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_state_util.py:35` | `merge_tool_test_task` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_state_util.py:53` | `mock_solver` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_stateful_code.py:36` | `sandbox_spec` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_stateful_code.py:54` | `custom_code_solver` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_stateful_code.py:150` | `huge_output_custom_code_solver` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_toolset_config.py:10` | `TestToolsetConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/astabench/tools/stateful_python.py:19` | `get_sandbox_jupyter` | Pinned implementation entry for the selected mechanism. |
| `official-code/astabench/tools/stateful_python.py:31` | `exec_python_session` | Pinned implementation entry for the selected mechanism. |
| `official-code/astabench/tools/stateful_python.py:49` | `python_session` | Pinned implementation entry for the selected mechanism. |
| `official-code/astabench/tools/search.py:24` | `make_paper_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/astabench/tools/search.py:51` | `make_snippet_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/astabench/tools/search.py:81` | `_query_s2_api` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_model_util.py:16` | `test_already_normalized` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/tools/test_model_util.py:37` | `test_known_models` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `eeb9bd72e95e56323bc283d215e302beff8b7007`. Paper page numbers refer to the fixed local proceedings PDF.
