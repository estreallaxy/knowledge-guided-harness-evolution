# Exact source anchors

## Selected mechanism

We propose DocSearch, a dependency-guided bi-level search framework that systematically exploits test-time feedback.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Method |
| Experimental setup | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | Experimental Setup |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.2. Main Results |
| Limitations or failure conditions | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | 2.3. Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/docsearch/agent/tools.py:28` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/agent/tools.py:36` | `tool_schemas` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/agent/tools.py:48` | `_resolve` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/agent/runtime.py:30` | `assemble_system` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/agent/runtime.py:50` | `_append_event` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/agent/runtime.py:59` | `_safe_done_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/test_executor.py:23` | `TestResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/test_executor.py:40` | `TestExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/java_test_executor.py:20` | `TestResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/java_test_executor.py:46` | `JavaTestExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/utils/metrics.py:7` | `solve_rate` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/utils/metrics.py:15` | `average_pass_rate` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/utils/metrics.py:22` | `solved_set` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/testgen/orchestrator.py:35` | `ModuleTestGenResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/testgen/orchestrator.py:46` | `generate_module_tests` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/testgen/orchestrator.py:96` | `_load_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/pipeline/evaluator.py:32` | `EntityResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/docsearch/pipeline/evaluator.py:53` | `EvaluationResult` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `48d3c4a2d0bd17b843f8751c2936f7a3ffd744db`. Paper page numbers refer to the fixed local proceedings PDF.
