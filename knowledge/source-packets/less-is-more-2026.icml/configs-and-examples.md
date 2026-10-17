# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LLaMA-Factory/examples/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/LLaMA-Factory/examples/README_zh.md` | Dependency, configuration, or usage evidence. |
| `official-code/LLaMA-Factory/scripts/api_example/test_image.py` | Dependency, configuration, or usage evidence. |
| `official-code/LLaMA-Factory/scripts/api_example/test_toolcall.py` | Dependency, configuration, or usage evidence. |
| `official-code/LLaMA-Factory/tests/check_license.py` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/verl_core/examples/data_preprocess/gsm8k_multiturn_w_tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/verl_core/examples/ppo_trainer/naive_chat_scheduler.py` | Dependency, configuration, or usage evidence. |
| `official-code/verl_core/examples/sglang_multiturn/config/tool_config/gsm8k_tool_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/verl_core/tests/sanity/check_license.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/LLaMA-Factory/src/llamafactory/webui/components/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
