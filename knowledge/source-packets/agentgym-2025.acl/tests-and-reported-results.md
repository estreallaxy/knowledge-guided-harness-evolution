# Tests and reported results

## Official verification entry points

- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/func_eval_fail.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/func_eval_success.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/func_url_func_1.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/func_url_func_2.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/html_content_element_exact_match.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/html_content_exact_match.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/html_content_url_comb.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/string_match.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/url_exact_match.json`
- `agentenv-alfworld/configs/mappings_test.json`
- `agentenv-searchqa/scripts/data_process/qa_search_test_merge.py`
- `agentenv-webarena/webarena/tests/test_browser_env/test_action_functionalities.py`
- `agentenv-webarena/webarena/tests/test_browser_env/test_actions.py`
- `agentenv-webarena/webarena/tests/test_browser_env/test_playwright_actions.py`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/test_evaluators.py`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/test_helper_functions.py`
- `agentenv-searchqa/agentenv_searchqa/reward_score/__init__.py`
- `agentenv-searchqa/agentenv_searchqa/reward_score/qa_em.py`
- `agentenv-searchqa/agentenv_searchqa/reward_score/qa_em_format.py`

## Published result anchors

- p. 5: Table 2: Statistics of AGENT G YM, including scenarios, count of task types, evaluation metric, instruction set size,
- p. 6: Table 3: Evaluating results on diverse tasks. AGENT T RAJ-SFT provides a base agent with basic ability and prior
- p. 8: Table 4: Evaluating results on out-of-domain tasks.
- p. 9: Table 6: Evaluating results on different models. the effectiveness of AGENT STA R on three differ-
- p. 18: Table 7: Evaluating performance and interactive rounds on diverse tasks. The first row of each method indicates
- p. 18: Table 8: Ablation study on sample number K and the training strategies. As shown in Figure 5, contin-
- p. 19: Table 9: Comparison between AGENT STA R and other can accurately determine its position and directly
- p. 21: Table 10: Prompt details for WebShop.
- p. 25: Table 11: Prompt details for ALFWorld.
- p. 26: Table 12: Prompt details for TextCraft.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | 2025, ACL long paper |
| Official open-source implementation | https://github.com/WooooDyy/AgentGym at `3ef9235d23e68e7c2920c5422ad957dc8ced5c6c` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
