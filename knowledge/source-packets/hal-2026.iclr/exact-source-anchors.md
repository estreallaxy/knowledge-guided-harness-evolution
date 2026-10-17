# Exact source anchors

## Selected mechanism

Orchestrate standardized parallel agent evaluations, capture cost and reliability signals, and publish comparable results.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.48; `paper/paper-iclr2026.txt` marker `===== PDF p.48 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.22; `paper/paper-iclr2026.txt` marker `===== PDF p.22 =====` | framework |
| Results and ablations | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | analysis |
| Limitations or failure conditions | PDF p.23; `paper/paper-iclr2026.txt` marker `===== PDF p.23 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agents/replicatorbench_agent/validator/aggregate_eval_scores.py:4` | `summarize_eval_execute` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/replicatorbench_agent/validator/aggregate_eval_scores.py:22` | `_to_float_or_none` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/replicatorbench_agent/validator/aggregate_eval_scores.py:35` | `summarize_eval_scores` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/USACO/USACOBench/evaluation/metrics.py:11` | `pass_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/USACO/USACOBench/evaluation/metrics.py:21` | `pass_at_k_codex` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/USACO/USACOBench/evaluation/metrics.py:31` | `_pass_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/replicatorbench_agent/generator/orchestrator_tool.py:22` | `PlanStep` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/replicatorbench_agent/generator/orchestrator_tool.py:31` | `ExecutionPlan` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/replicatorbench_agent/generator/orchestrator_tool.py:42` | `_detect_lang_from_ext` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/reliability_eval/test_safety_metrics.py:10` | `_make_run_with_safety` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/reliability_eval/test_safety_metrics.py:40` | `TestComputeSafetyMetricsNoViolations` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/reliability_eval/test_safety_metrics.py:57` | `TestComputeSafetyMetricsWithViolations` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/USACO/evaluate.py:19` | `judge_fn_solve` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/USACO/evaluate.py:35` | `evaluate_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/USACO/evaluate.py:141` | `evaluate_ss` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/replicatorbench_agent/validator/evaluate_replication_preregistration.py:12` | `extract_text_from_pdf` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/replicatorbench_agent/validator/evaluate_replication_preregistration.py:17` | `extract_text_from_docx` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/replicatorbench_agent/validator/evaluate_replication_preregistration.py:22` | `load_report_text` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `16bb03ebc11577fb5ea6dc8bb6c968387085e6aa`. Paper page numbers refer to the fixed local proceedings PDF.
