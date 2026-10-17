# Exact source anchors

## Selected mechanism

Convert open-ended human feedback into clustered, executable trajectory metrics and LLM-as-judge evaluations.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Experiments |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/packages/osw-data/src/osw_data/metrics.py:7` | `MetricSetMetadata` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/osw-data/src/osw_data/metrics.py:15` | `Metric` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/osw-data/src/osw_data/metrics.py:22` | `MetricSet` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/autolibra-core/src/autolibra_core/evaluators/llm_evaluator.py:13` | `_make_snake_case` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/autolibra-core/src/autolibra_core/evaluators/llm_evaluator.py:17` | `_make_evaluation_result_class` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/autolibra-core/src/autolibra_core/evaluators/llm_evaluator.py:38` | `_load_llm_eval_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/autolibra-core/src/autolibra_core/evaluators/coverage_evaluator.py:18` | `_sanitize_string` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/autolibra-core/src/autolibra_core/evaluators/coverage_evaluator.py:31` | `create_aspect_traits_match_pydantic_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/autolibra-core/src/autolibra_core/evaluators/coverage_evaluator.py:61` | `match_aspects_and_traits` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/training/prompt_improver_direct_data.py:33` | `AutoLibraPromptImprover` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/training/prompt_improver_direct_data.py:1593` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/osw-data/tests/test_metrics.py:11` | `sample_metric` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/osw-data/tests/test_metrics.py:22` | `sample_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/osw-data/tests/test_metrics.py:41` | `metric_set` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/osw-data/src/osw_data/trajectory.py:12` | `MediaType` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/osw-data/src/osw_data/trajectory.py:23` | `PointType` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/osw-data/src/osw_data/trajectory.py:30` | `MediaReference` | Pinned implementation entry for the selected mechanism. |
| `official-code/packages/autolibra-core/src/autolibra_core/configs/__init__.py:6` | `AutoLibraEvalSettings` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `64cf838004e51a9c6a398409d908b55c0b9d08cd`. Paper page numbers refer to the fixed local proceedings PDF.
