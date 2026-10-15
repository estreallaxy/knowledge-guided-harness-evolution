# Tests and reported results

## Official verification entry points

- `tests/test_evaluation_harness/configs/exact_image_failure.json`
- `tests/test_evaluation_harness/configs/exact_image_resize_failure_1.json`
- `tests/test_evaluation_harness/configs/exact_image_resize_failure_2.json`
- `tests/test_evaluation_harness/configs/exact_image_resize_template.json`
- `tests/test_evaluation_harness/configs/exact_image_success.json`
- `tests/test_evaluation_harness/configs/func_eval_fail.json`
- `tests/test_evaluation_harness/configs/func_eval_success.json`
- `tests/test_evaluation_harness/configs/func_url_func_1.json`
- `tests/test_evaluation_harness/configs/func_url_func_2.json`
- `tests/test_evaluation_harness/configs/html_content_element_exact_match.json`
- `tests/test_evaluation_harness/configs/html_content_exact_match.json`
- `tests/test_evaluation_harness/configs/html_content_url_comb.json`
- `tests/test_evaluation_harness/configs/html_required_values_failure_1.json`
- `tests/test_evaluation_harness/configs/html_required_values_success_1.json`
- `tests/test_evaluation_harness/configs/image_evaluator_yes.json`
- `tests/test_evaluation_harness/configs/image_evaluator_yes_direct_img.json`
- `tests/test_evaluation_harness/configs/image_evaluator_yes_no.json`
- `tests/test_evaluation_harness/configs/string_match.json`
- `tests/test_evaluation_harness/configs/url_exact_match.json`
- `tests/test_browser_env/test_action_functionalities.py`
- `tests/test_browser_env/test_actions.py`
- `tests/test_browser_env/test_playwright_actions.py`
- `tests/test_evaluation_harness/test_exact_evaluators.py`
- `tests/test_evaluation_harness/test_helper_functions.py`
- `scripts/generate_test_data.py`
- `tests/conftest.py`
- `evaluation_harness/__init__.py`
- `evaluation_harness/evaluators.py`

## Published result anchors

- p. 3: Table 1: Set of possible actions A.
- p. 6: Table 2: Various evaluation metrics to assign reward r(s, a) ∈ R : S × A → {0, 1}. Our execution-based reward
- p. 8: Table 3: Success rates of baseline LLM and VLM agents on VisualWebArena.
- p. 9: Table 4: Success rate (SR) of GPT-4V (SoM) across success rates on VisualWebArena. Our quantita-
- p. 13: Table 5: Success rates of recent LLM and VLM agents on VisualWebArena.
- p. 13: Table 6: Performance with different number of in-

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ACL 2024 |
| Official open-source implementation | https://github.com/web-arena-x/visualwebarena at `89f5af29305c3d1e9f97ce4421462060a70c9a03` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
