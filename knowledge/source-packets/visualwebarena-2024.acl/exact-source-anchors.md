# Exact source anchors

## Selected mechanism

Combine webpage screenshots with accessibility/state observations, a typed browser action space, deterministic setup, and functional evaluators.

## Paper anchors

- p. 1: limitations of text-based LLM agents, gaps in
- p. 3: framework are provided as standalone self-hosted content can be represented in several ways:
- p. 4: 3.3 Evaluation a reward of 1 if the output is “correct”.2 This
- p. 4: evaluation paradigm of WebArena. These allow asking the user to add a comment describing

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `CITATION.cff`
- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.cfg`
- `setup.py`
- `environment_docker/README.md`
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
- `agent/prompts/jsons/p_cot_id_actree_2s.json`
- `agent/prompts/jsons/p_cot_id_actree_2s_no_na.json`
- `agent/prompts/jsons/p_cot_id_actree_3s.json`
- `agent/prompts/jsons/p_multimodal_cot_id_actree_3s.json`
- `agent/prompts/jsons/p_som_cot_id_actree_3s.json`
- `agent/prompts/raw/p_cot_id_actree_2s.py`
- `agent/prompts/raw/p_cot_id_actree_2s_no_na.py`
- `agent/prompts/raw/p_cot_id_actree_3s.py`
- `agent/prompts/raw/p_multimodal_cot_id_actree_3s.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The reusable mechanism is the multimodal environment interface and evaluator, with no parameter training. Main-paper experiments and the code expose image observations, actions, resets, and scoring.

## Symbol-level code anchors

- `run.py:66` — `config`
- `run_demo.py:61` — `config`
- `agent/agent.py:29` — `Agent`
- `browser_env/actions.py:46` — `ParsedPlaywrightCode`
- `browser_env/async_envs.py:17` — `AsyncScriptBrowserEnv`
- `browser_env/auto_login.py:53` — `is_expired`
- `browser_env/envs.py:44` — `PlaywrightScript`
- `browser_env/helper_functions.py:37` — `get_render_action`
- `browser_env/processors.py:43` — `remove_unicode`
- `browser_env/utils.py:18` — `DetachedPage`
- `evaluation_harness/evaluators.py:51` — `Evaluator`
- `evaluation_harness/helper_functions.py:23` — `PseudoPage`
