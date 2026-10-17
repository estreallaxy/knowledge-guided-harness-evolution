# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/aviary_gpt4/aviary_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/chatgpt/basic_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/chatgpt_fn/basic_function_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/claude/basic_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/claude_3_opus_ranking/ranking_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/claude_ranking/ranking_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/gpt-3.5-turbo-1106_ranking/ranking_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/gpt4_turbo_clf/basic_clf_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/gpt4_turbo_cot_clf/basic_clf_cot_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/guanaco_33b/basic_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/llama-3.3-70B-instruct-turbo/readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/lmsys_gpt4/lmsys_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/oasst_pythia_12b/basic_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/test/configs.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/text_davinci_003/basic_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/evaluators_configs/weighted_alpaca_eval_vllm_llama3_70b/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/models_configs/Contextual-KTO-Mistral-PairRM-Verified/prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/models_configs/Contextual-KTO-Mistral-PairRM/prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/models_configs/Ein-70B-v0.1/prompt.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/winrate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/helpers.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/glm_winrate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/decoders/cache.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/annotators/pairwise_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/decoders/test.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/Alpaca_Eval2/tests/test_pairwise_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/constants.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
