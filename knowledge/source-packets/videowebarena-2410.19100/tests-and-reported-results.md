# Tests and reported results

All values below are reported by the paper; they are not local reproduction results.

| System | Metric | Reported value | Source |
| --- | --- | --- | --- |
| GPT-4o summary agent | Factual final / intermediate | 13.3% / 36.8% | Table 6, PDF p.9 |
| GPT-4o 30-frame agent | Factual final / intermediate | 11.0% / 45.8% | Table 6, PDF p.9 |
| Human | Factual final / intermediate | 73.9% / 79.3% | Table 6, PDF p.9 |
| GPT-4o summary with tutorial | WebArena / VisualWebArena final | 13.8% / 11.6% | Table 7, PDF p.9 |
| GPT-4o without tutorial | WebArena / VisualWebArena final | 14.9% / 19.8% | Table 7, PDF p.9 |

## Evidence boundary

The code snapshot omits task configurations and videos. The paper reports that intermediate understanding and final success are weakly coupled; neither score should substitute for the other.

## Current packet validation

| Check | Status |
| --- | --- |
| Paper PDF and text | Present; the text was extracted from the fixed PDF for section and table review. |
| Official code identity | Repository, branch, upstream revision and retrieval date are recorded in `source-packet.json`. |
| Core mechanism code | Present and linked from `exact-source-anchors.md`. |
| Secrets and credentials | Excluded from the packet. |
| Benchmark answers or target state | Excluded from the packet. |
| Training requirement for selected mechanism | None; no ExecutorLLM, OptimizerLLM or task-specific neural module is trained. |
| End-to-end benchmark rerun | Not performed for this knowledge packet. |
| Target-harness migration effect | Unknown until evaluated under the project's common protocol. |

## Additional retained verification anchors

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
