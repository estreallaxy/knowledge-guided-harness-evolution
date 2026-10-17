# Exact source anchors

## Selected mechanism

To bridge this gap, we present LeVer, the first trustworthy smart contract synthesis framework that integrates LLM-based generation with Lean-based auto-formalization and Verification.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | design |
| Experimental setup | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 5 Experiments |
| Results and ablations | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | 5.3 Ablation |
| Limitations or failure conditions | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | limitation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/core/pipeline/metrics.py:4` | `MetricsTracker` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/agents.py:19` | `FatalLLMError` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/agents.py:23` | `is_fatal_llm_error` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/agents.py:45` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/pipeline/context.py:3` | `PipelineContext` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/pipeline/workflows.py:13` | `_read_iteration_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/pipeline/workflows.py:22` | `_write_pipeline_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/pipeline/workflows.py:83` | `workflow_from_requirement` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/config.py:42` | `get_simulation_agents` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/pipeline/lean_validation.py:5` | `validate_generated_lean` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/logger.py:5` | `Logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/formal_verifier.py:6` | `FormalVerifier` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/regression_runner.py:6` | `RegressionTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/main_pipeline.py:30` | `_safe_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/main_pipeline.py:38` | `_build_parser` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/main_pipeline.py:65` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/structured_logging.py:14` | `utc_timestamp` | Pinned implementation entry for the selected mechanism. |
| `official-code/core/structured_logging.py:23` | `clean_ansi` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `4a7e8e6588a7cfe186f1d1ba9c90a7e675fbd0cc`. Paper page numbers refer to the fixed local proceedings PDF.
