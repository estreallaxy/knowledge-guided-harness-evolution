# Configs and examples

## Paper configuration

| Configuration surface | Paper setting | Source |
| --- | --- | --- |
| Task families | 400 factual-retention intents plus skill-retention tasks | §3.5–3.6, PDF pp.6–7 |
| Web state | Set-of-Marks accessibility-tree representation | §4, PDF pp.7–8 |
| Frame baseline | 1 frame/s, capped at 60, plus Whisper transcript | §4.2, PDF p.8 |
| Evaluation | Intermediate video-intent score plus binary final environment score | §3.7, PDF p.7 |
| Actions | Browser actions listed in Table 4 | §3.1, PDF p.5 |

## Official entry point

```bash
git clone https://github.com/ljang0/videowebarena.git
git -C videowebarena checkout d79b968a5e5a5c157e099ab6343f701a261ade55
```

The local snapshot is intended for mechanism inspection and adaptation. Run the upstream setup from the fixed revision when reproducing the full benchmark because datasets, service state, VM images, secrets and task answers are intentionally absent here.

## Harness migration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task instruction and initial environment state | Reset the isolated environment and create a run identifier. | Initial observation plus immutable task metadata. |
| Model action or tool call | Validate the action against the exposed interface, execute it, and record the result. | Typed observation, execution status, timing and error evidence. |
| Termination or step limit | Freeze the final environment state and call the task evaluator. | Final score, evaluator details, full trajectory and resource usage. |
| Repeated trial | Restore the same initial state while changing only the declared seed or sampling source. | Per-trial result and reliability statistics without cross-trial state leakage. |

## Additional retained configuration anchors

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
