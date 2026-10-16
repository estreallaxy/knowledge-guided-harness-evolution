# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/evaluation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/evaluation/patch_selection/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/evaluation/setup.sh` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/examples/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/examples/continuous_runner_example.py` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/examples/simple_usage.py` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/tests/utils/test_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/trae_agent/agent/docker_manager.py` | Dependency, configuration, or usage evidence. |
| `official-code/zerorepo/code_gen/trae-agent/trae_agent/tools/docker_tool_executor.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/zerorepo/code_gen/trae-agent/evaluation/patch_selection/trae_selector/tools/tools/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/zerorepo/code_gen/trae-agent/trae_agent/tools/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
