# Tests and reported results

## Official verification entry points

- `Ego4d/SoM/benchmark/README.md`
- `VisualWebArena/agent/prompts/retrieval_augmented_prompt.py`
- `VisualWebArena/agent/prompts/retrieval_augmented_prompt_faiss.py`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_failure.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_resize_failure_1.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_resize_failure_2.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_resize_template.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/exact_image_success.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/func_eval_fail.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/func_eval_success.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/func_url_func_1.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_content_element_exact_match.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_content_exact_match.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_content_url_comb.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_required_values_failure_1.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/html_required_values_success_1.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/image_evaluator_yes.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/image_evaluator_yes_direct_img.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/image_evaluator_yes_no.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/string_match.json`
- `VisualWebArena/tests/test_evaluation_harness/configs/url_exact_match.json`
- `VisualWebArena/run_eval.py`
- `TEACh/SOLQ/configs/r50_solq_eval.sh`

## Published result anchors

- p. 8: Table 2: Results in VisualWebArena. ICAL
- p. 8: Table 1: Evaluation on TEACh unseen valida- Marks. Ablation studies were conducted with
- p. 10: Table 1. We conclude: ory. First half (blue) versus second half (orange)

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2024 |
| Official open-source implementation | https://github.com/Gabesarch/ICAL at `f4588d55f80aa80f0e21fce5adcb4b998bf4e4c3` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
