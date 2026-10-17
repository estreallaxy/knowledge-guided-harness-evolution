# Exact source anchors

## Selected mechanism

We introduce NCP-Bench , a benchmark of 100 narrative environments derived from movie synopses.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5.2. Main Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 6. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/ncpbench/evaluator_prompts.py:19` | `EvaluationPrompts` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ncpbench/evaluator_prompts.py:29` | `load_evaluation_prompts` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ncpbench/evaluator_prompts.py:42` | `render_fact_update` | Pinned implementation entry for the selected mechanism. |
| `official-code/reference-methods/hiagent/src/ncpbench_reference_hiagent/hiagent_prompts.py:41` | `_replace_output_format_section` | Pinned implementation entry for the selected mechanism. |
| `official-code/reference-methods/hiagent/src/ncpbench_reference_hiagent/hiagent_prompts.py:57` | `build_hiagent_turn_context` | Pinned implementation entry for the selected mechanism. |
| `official-code/reference-methods/hiagent/src/ncpbench_reference_hiagent/hiagent_prompts.py:70` | `_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/reference-methods/hiagent/src/ncpbench_reference_hiagent/config.py:9` | `HiAgentRuntimeConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ncpbench/metrics.py:12` | `EpisodeMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ncpbench/metrics.py:30` | `AggregateMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ncpbench/metrics.py:45` | `MetricInputError` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ncpbench/evaluator.py:30` | `AuditorClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ncpbench/evaluator.py:38` | `TurnAuditContext` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/ncpbench/evaluator.py:50` | `FactUpdate` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_metrics.py:14` | `MetricsTests` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_metrics.py:73` | `_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_evaluator_protocol.py:18` | `RecordedAuditor` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_evaluator_protocol.py:29` | `EvaluatorProtocolTests` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_evaluator_protocol.py:85` | `_context` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `780aeb559ce216a57cbd934b5a20bfd35018c4f6`. Paper page numbers refer to the fixed local proceedings PDF.
