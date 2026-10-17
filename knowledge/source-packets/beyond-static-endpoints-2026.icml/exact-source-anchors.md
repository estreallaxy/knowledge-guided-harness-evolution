# Exact source anchors

## Selected mechanism

We present ToolPro, which represents an agent’s tool intent as an executable tool program that compactly encodes multi-step service interactions with explicit effect types.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 60 Method |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4. Experiments |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/core/stepwise_executor.py:22` | `StepwiseRunResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/stepwise_executor.py:28` | `StepwiseExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/stepwise_executor.py:55` | `parse_stepwise_plan_from_input` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/default_mcp_write_tool_meta.py:82` | `merge_write_tool_meta` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/tool_program_validator.py:14` | `collect_structural_violations` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/tool_program_validator.py:81` | `validate_mcp_calls_have_adjacent_markers` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/stepwise_agent_handler.py:27` | `_compose_task_description` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/stepwise_agent_handler.py:69` | `_compact_tool_spec` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/stepwise_agent_handler.py:79` | `_load_available_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/transaction_context.py:19` | `TransactionContextManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/wasm_runtime.py:29` | `mcp_call_tool_timeout_seconds` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/wasm_runtime.py:44` | `WasmRuntime` | Pinned implementation entry for the selected mechanism. |
| `official-code/config.py:9` | `Config` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiment/calculate/tools/run_analysis.py:18` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/debug_config.py:9` | `DebugConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiment/calculate/tools/performance_analyzer.py:23` | `PerformanceAnalyzer` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiment/calculate/tools/performance_analyzer.py:376` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiment/calculate/tools/extract_experiment_results.py:20` | `ExperimentDataExtractor` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9a634427fa3cc92fcf4d57206e6c2aeb681b66c2`. Paper page numbers refer to the fixed local proceedings PDF.
