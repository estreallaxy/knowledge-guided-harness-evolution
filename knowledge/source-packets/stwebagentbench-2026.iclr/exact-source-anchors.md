# Exact source anchors

## Selected mechanism

Evaluate web-agent safety and trustworthiness with executable enterprise scenarios and explicit policy checks.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | approach |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Results |
| Limitations or failure conditions | PDF p.17; `paper/paper-iclr2026.txt` marker `===== PDF p.17 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/stwebagentbench/test_eval/test_benchmark_validation.py:79` | `_load_tasks` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_benchmark_validation.py:84` | `_extract_must_include_terms` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_benchmark_validation.py:91` | `TestSchemaIntegrity` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_evaluator_comb.py:14` | `TestEvaluatorComb` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_evaluator_comb.py:52` | `TestSafetyEvaluatorComb` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_url_evaluator.py:14` | `TestURLEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_url_evaluator.py:89` | `TestURLEvaluatorQueryParams` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_string_evaluator.py:14` | `TestStringEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_string_evaluator.py:160` | `TestStringEvaluatorMultipleMustInclude` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_string_evaluator.py:207` | `TestStringEvaluatorCaseSensitivity` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_html_content_evaluator.py:23` | `_make_trace` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_html_content_evaluator.py:29` | `_create_mock_page` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_html_content_evaluator.py:37` | `TestHTMLContentEvaluatorMustInclude` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_action_evaluator.py:14` | `TestActionEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/test_eval/test_content_validation.py:14` | `TestInputHallucinationEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/evaluation_harness/evaluators.py:73` | `create_report_point` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/evaluation_harness/evaluators.py:101` | `validate_policy_schema` | Pinned implementation entry for the selected mechanism. |
| `official-code/stwebagentbench/evaluation_harness/evaluators.py:188` | `_clean_url` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `67f56dd7df9eca1646c9e49407b087e950aa1e77`. Paper page numbers refer to the fixed local proceedings PDF.
