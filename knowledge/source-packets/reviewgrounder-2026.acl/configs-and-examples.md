# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/shared/configs/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/shared/configs/llm_service_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/shared/configs/prompts.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/src/evaluator/configs.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/gradio_app/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/reviewer_agent/cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/reviewer_agent/main_pipeline.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/reviewer_agent/main_pipeline_concurrent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
