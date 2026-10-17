# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/desktop_env/evaluators/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/coact/autogen/coding/docker_commandline_code_executor.py` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/coact/autogen/coding/jupyter/docker_jupyter_server.py` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/coact/autogen/interop/litellm/litellm_config_factory.py` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/coact/autogen/llm_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/maestro/maestro/controller/config_manager.py` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/maestro/maestro/debug_system/example_usage.py` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/maestro/maestro/debug_system/logging_setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/maestro/tools/new_tools_config.json` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/mm_agents/anthropic/tools/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
