# Exact source anchors

## Selected mechanism

Compositional task generation, certified oracle and validator pairs, automatic ground-truth traces, backend setup/teardown, and BrowserGym integration.

## Paper anchors

- p. 7: 4.1 Evaluation Curriculum: Standardizing WorkArena++ as a Benchmark
- p. 8: Results on WorkArena L1, WebArena and MiniWoB are extracted from Drouin et al. [2024]. Human evaluation
- p. 8: results in Tab. 2 under the Human Curriculum column, along with the corresponding performance of
- p. 10: 7 Limitations and Potential Societal Impacts
- p. 10: Limitations While WorkArena++ includes diverse and realistic workflows, it does not exhaustively
- p. 11: approach for learning to control computers. In International Conference on Machine Learning
- p. 37: Algorithm 1 Agent Curriculum for WorkArena++ Benchmark

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

The acceptance and transfer decision is limited to the inference-time mechanism described above. Archival NeurIPS track; generation and validation machinery are training-free.

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
