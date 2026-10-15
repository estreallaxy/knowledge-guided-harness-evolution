# Exact source anchors

## Paper

| Mechanism or evidence | Exact location | Supported claim and boundary |
| --- | --- | --- |
| Benchmark runtime and action space | §3–3.2 and Table 4, PDF pp.4–5 | Extends realistic web environments with video-conditioned tasks and a bounded browser action vocabulary. |
| Observation and task decomposition | §3.3–3.6, PDF pp.5–7 | Defines accessibility-tree/web state plus video, frames or summaries and separates intermediate video intent from final agent success. |
| Two-level evaluation | §3.7, PDF p.7 | Uses an intermediate string evaluator for extracted video information and a final environment-state evaluator for task completion. |
| Context adapters | §4.1–4.3, PDF pp.7–8 | Compares whole-video, sampled-frame plus transcript, and task-conditioned summary injection. |
| Results and failure boundary | §5 and Tables 6–8, PDF pp.8–10 | Shows that correct intermediate extraction often fails to produce correct action sequences and that tutorials can hurt agents. |

## Official code

The paths below refer to the retained snapshot of [https://github.com/ljang0/videowebarena](https://github.com/ljang0/videowebarena) at upstream revision `d79b968a5e5a5c157e099ab6343f701a261ade55`.

| Mechanism or evidence | Snapshot path | Role |
| --- | --- | --- |
| Browser environment | `browser_env/envs.py; browser_env/async_envs.py` | Implements reset, step, state observations and evaluator-triggered rewards. |
| Video-conditioned agents | `agent/agent.py` | Loads task video context and exposes video, frame and summary variants through a common agent lifecycle. |
| Evaluation composition | `evaluation_harness/evaluators.py` | Combines URL, string, HTML, image and state checks into final task reward. |
| Video adapters | `video_understanding` | Provides frame sampling, transcription and summary preparation used by the three baselines. |
| Execution entry | `run.py; run_demo.py` | Connects model, agent, browser environment, task lifecycle and output trace. |

The snapshot deliberately omits benchmark answers, task-specific target state, credentials, generated traces, datasets, model weights and files that are unnecessary to inspect the selected mechanism.

## Additional retained implementation anchors

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

## Symbol-level code anchors

- `run.py:69` — `config`
- `run_demo.py:61` — `config`
- `agent/agent.py:30` — `Agent`
- `browser_env/actions.py:46` — `ParsedPlaywrightCode`
- `browser_env/async_envs.py:17` — `AsyncScriptBrowserEnv`
- `browser_env/auto_login.py:72` — `is_expired`
- `browser_env/envs.py:44` — `PlaywrightScript`
- `browser_env/helper_functions.py:37` — `get_render_action`
- `browser_env/processors.py:43` — `remove_unicode`
- `browser_env/utils.py:18` — `DetachedPage`
- `evaluation_harness/evaluators.py:51` — `Evaluator`
- `evaluation_harness/helper_functions.py:23` — `PseudoPage`
