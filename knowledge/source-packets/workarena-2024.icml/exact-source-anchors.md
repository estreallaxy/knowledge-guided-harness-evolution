# Exact source anchors

## Selected mechanism

BrowserGym standardizes reset/step/observation/action/termination and WorkArena supplies reproducible task state and validation. The extractable contribution is environment/session harnessing.

## Paper anchors

- p. 2: evaluation of web agents, compatible with previous bench- actions from 137 websites curated by human annotators. Sim-
- p. 6: experiment with use action history which includes in

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `CITATION.cff`
- `LICENSE`
- `README.md`
- `pyproject.toml`
- `requirements.txt`
- `dev/requirements.txt`
- `src/browsergym/workarena/tasks/scripts/README.md`
- `tests/test_random_config_generation.py`
- `tests/test_task_from_config.py`
- `src/browsergym/workarena/data_files/task_configs/dashboard_retrieval_minmax_task.json`
- `src/browsergym/workarena/data_files/task_configs/dashboard_retrieval_value_task.json`
- `src/browsergym/workarena/data_files/task_configs/report_retrieval_minmax_task.json`
- `src/browsergym/workarena/data_files/task_configs/report_retrieval_value_task.json`
- `src/workarena_test.py`
- `tests/conftest.py`
- `tests/test_api.py`
- `tests/test_compositional.py`
- `tests/test_compositional_binding.py`
- `tests/test_compositional_utils.py`
- `tests/test_filter_list_task.py`
- `tests/test_instance_preconditions.py`
- `tests/test_snow_instance.py`
- `tests/test_task_general.py`
- `tests/test_task_setup.py`
- `tests/test_utils.py`
- `tests/test_validate.py`
- `tests/utils.py`
- `make_human_eval_curriculum.py`
- `src/browsergym/workarena/human_eval/tool.py`
- `dev/environment.yaml`
- `scripts/make_human_eval_curriculum.py`
- `src/wa_action_traces.py`
- `src/browsergym/workarena/config.py`
- `src/browsergym/workarena/data_files/task_configs/all_menu.json`
- `src/browsergym/workarena/data_files/task_configs/impersonation_users.json`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. BrowserGym standardizes reset/step/observation/action/termination and WorkArena supplies reproducible task state and validation. The extractable contribution is environment/session harnessing.

## Symbol-level code anchors

- `tests/test_random_config_generation.py:90` — `test_cheat_from_random_config`
- `tests/test_task_from_config.py:93` — `generic_task_cheat_test`
- `tests/conftest.py:9` — `pytest_collection_modifyitems`
- `tests/test_api.py:13` — `test_set_user_preference`
- `tests/test_compositional.py:23` — `warn_retry`
- `tests/test_compositional_binding.py:16` — `StubSubtask`
- `tests/test_compositional_utils.py:24` — `test_knapsack`
- `tests/test_filter_list_task.py:18` — `test_validate_filter_list_task`
- `tests/test_instance_preconditions.py:85` — `instance_entry`
- `tests/test_snow_instance.py:28` — `snow_instance_entry`
- `tests/test_task_general.py:31` — `snow_instance_entry`
- `tests/test_task_setup.py:28` — `test_add_to_cart_disabled`
