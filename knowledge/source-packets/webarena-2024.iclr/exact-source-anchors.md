# Exact source anchors

## Selected mechanism

Run agents against resettable self-hosted websites with typed browser actions, structured observations, task setup, and functional/state evaluators.

## Paper anchors

- p. 3: Implementation We leveraged open-source libraries relevant to each category to build our own
- p. 6: evaluation. The corresponding prompt details are provided in Appendix A.7. The fuzzy_match
- p. 15: implementation, confining our focus to the northeast US region due to data storage constraints. We
- p. 16: evaluation time.
- p. 17: results, we provide the results of GPT-3.5- TURBO -16 K -0613 with temperature 0.0 in Table 5 and
- p. 18: ablation studies.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `CITATION.cff`
- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.cfg`
- `setup.py`
- `environment_docker/README.md`
- `resources/README.md`
- `agent/prompts/README.md`
- `agent/prompts/raw/p_cot_id_actree_2s.py`
- `agent/prompts/raw/p_cot_id_actree_2s_no_na.py`
- `agent/prompts/raw/p_direct_id_actree_2s.py`
- `agent/prompts/raw/p_direct_id_actree_2s_no_na.py`
- `agent/prompts/raw/p_direct_id_actree_3s_llama.py`
- `tests/test_browser_env/test_action_functionalities.py`
- `tests/test_browser_env/test_actions.py`
- `tests/test_browser_env/test_playwright_actions.py`
- `.pre-commit-config.yaml`
- `browser_env/env_config.py`
- `llms/lm_config.py`
- `scripts/generate_test_data.py`
- `tests/conftest.py`
- `agent/prompts/__init__.py`
- `agent/prompts/prompt_constructor.py`
- `agent/prompts/to_json.py`
- `parallel_run.sh`
- `run.py`
- `agent/__init__.py`
- `agent/agent.py`
- `browser_env/actions.py`
- `evaluation_harness/__init__.py`
- `evaluation_harness/evaluators.py`
- `evaluation_harness/helper_functions.py`
- `scripts/check_error_runs.py`
- `config_files/examples/1.json`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. It provides a complete environment/harness rather than a trained policy. The paper gives failure analysis; the official code includes Docker sites, browser environment, prompt constructors, action parser, and evaluators.

## Symbol-level code anchors

- `tests/test_browser_env/test_action_functionalities.py:19` — `test_frame_locator`
- `tests/test_browser_env/test_actions.py:6` — `test_is_equivalent`
- `tests/test_browser_env/test_playwright_actions.py:12` — `test_frame_locator`
- `llms/lm_config.py:12` — `LMConfig`
- `scripts/generate_test_data.py:8` — `main`
- `tests/conftest.py:13` — `script_browser_env`
- `agent/prompts/prompt_constructor.py:14` — `Instruction`
- `agent/prompts/to_json.py:8` — `run`
- `run.py:59` — `config`
- `agent/agent.py:28` — `Agent`
- `browser_env/actions.py:45` — `ParsedPlaywrightCode`
- `evaluation_harness/evaluators.py:32` — `Evaluator`
