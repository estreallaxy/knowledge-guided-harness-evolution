# Tests and reported results

## Official verification entry points

- `tests/test_feedback_agent.py`
- `tests/test_search_tree.py`
- `moatless/actions/run_tests.py`
- `moatless/runtime/testbed.py`
- `tests/test_file_context.py`
- `tests/test_json_extraction.py`
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

## Published result anchors

- p. 8: Table 1: Resolve Rate Comparison, SWE-bench Lite
- p. 18: Table 2: MCTS Hyperparameters
- p. 30: Table 3: Cost comparison (USD) between Moatless-Adapted and SWE-Search
- p. 30: Table 4: Performance comparison (%) between SWE-Search and compute-matched baselines

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2025 |
| Official open-source implementation | https://github.com/aorwall/moatless-tree-search at `bc66ea64e3fe96cf3c90f197b4bab9aaa15e1eb9` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
