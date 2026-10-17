# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/emoa/src/emoa/router/config/exp1.py` | Dependency, configuration, or usage evidence. |
| `official-code/emoa/src/emoa/router/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_api_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_attack.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_base_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_chat_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_chat_agent_baseline.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_chat_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_codeagent.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_corebench_2409_longcontext.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_edgellm_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_llm_compression.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_lmdeploy_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_math_verify.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_mmlu_with_zero_retriever_overwritten.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/examples/archived_scripts/eval_multi_prompt_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/tools/compare_configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/tools/list_configs.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/opencompass/examples/archived_scripts/eval_api_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_attack.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_base_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_chat_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_chat_agent_baseline.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_chat_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_codeagent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_corebench_2409_longcontext.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_edgellm_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_llm_compression.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_lmdeploy_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_math_verify.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_mmlu_with_zero_retriever_overwritten.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/opencompass/examples/archived_scripts/eval_multi_prompt_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
