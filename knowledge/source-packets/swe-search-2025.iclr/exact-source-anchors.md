# Exact source anchors

## Selected mechanism

Multi-agent MCTS over repository edits, LLM numerical/qualitative value estimates, state snapshots, backtracking, and iterative patch refinement. No parameter update is required.

## Paper anchors

- p. 2: approach dynamically, ensuring the agent can revise its course when faced with new challenges or
- p. 5: limitations of different state types (e.g., Search, Edit, Plan), helping the Action Agent better
- p. 6: algorithm mirrors:
- p. 7: Evaluation Metrics We use two metrics: resolve rate (Pass@1) and Pass@5. Resolve rate is the
- p. 7: results on SWE-bench Lite to ensure a fair and consistent comparison.
- p. 7: Implementation Details For consistency, we use identical prompts across all models. In SWE-
- p. 17: results are provided to the state. The tests are then run in Docker images built via the SWE-bench
- p. 22: evaluation will focus on whether the search action was well-constructed, whether the re-
- p. 22: Evaluation Criteria:
- p. 24: Evaluation Criteria:
- p. 26: Evaluation Criteria:
- p. 27: Evaluation Criteria

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `tests/test_feedback_agent.py`
- `tests/test_search_tree.py`
- `moatless/actions/run_tests.py`
- `moatless/runtime/testbed.py`
- `tests/test_file_context.py`
- `tests/test_json_extraction.py`
- `moatless/search_tree.py`
- `moatless/actions/apply_change_and_test.py`
- `moatless/benchmark/evaluation_config.py`
- `moatless/benchmark/test_evaluation_v2.py`
- `tests/actions/test_action.py`
- `tests/actions/test_create_file.py`
- `tests/actions/test_edit.py`
- `tests/actions/test_find_function.py`
- `tests/actions/test_insert_line.py`
- `tests/actions/test_string_replace.py`
- `tests/actions/test_view_code.py`
- `tests/context/test_similarity.py`
- `tests/verify/test_testbed.py`
- `pytest.ini`
- `tests/conftest.py`
- `tests/integration_test.py`
- `tests/test_chat.py`
- `tests/test_completion.py`
- `tests/test_completion_integration.py`
- `tests/test_message_history.py`
- `tests/test_node.py`
- `tests/test_repository.py`
- `tests/test_selector.py`
- `tests/test_value_function.py`
- `tests/traj_haiku.json`
- `moatless/actions/search_base.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Multi-agent MCTS over repository edits, LLM numerical/qualitative value estimates, state snapshots, backtracking, and iterative patch refinement. No parameter update is required.

## Symbol-level code anchors

- `tests/test_feedback_agent.py:12` — `TestFeedbackAgent`
- `tests/test_search_tree.py:18` — `test_search_tree_dump_and_load`
- `moatless/actions/run_tests.py:21` — `RunTestsArgs`
- `moatless/runtime/testbed.py:21` — `TestbedEnvironment`
- `tests/test_file_context.py:18` — `test_file_context_to_dict`
- `tests/test_json_extraction.py:3` — `test_extract_single_json_codeblock`
- `moatless/search_tree.py:33` — `SearchTree`
- `moatless/actions/apply_change_and_test.py:20` — `ChangeType`
- `moatless/benchmark/evaluation_config.py:80` — `get_single_instance_config`
- `moatless/benchmark/test_evaluation_v2.py:26` — `DateTimeEncoder`
- `tests/actions/test_action.py:15` — `test_action_schema`
- `tests/actions/test_create_file.py:9` — `repository`
