# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/config/base_config/eval_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/base_config/multiagent_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/bedrock.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/bedrock_opus_4_7.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/claude.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/gemini.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/gemini_3_1_pro.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/openai.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/openai_gpt_5_4.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/opensource_api.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/opensource_vllm.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/integration/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/src/utils/config_loader.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/integration/cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/utils/evaluation/eval_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/utils/evaluation/evaluate_arguments.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/utils/evaluation/evaluate_workflow_as_DAG.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
