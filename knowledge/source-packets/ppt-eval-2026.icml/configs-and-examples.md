# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/SETUP.md` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/configs/claude-4-sonnet.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/configs/opencua-32b.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/configs/opencua-72b.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/configs/opencua-7b.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/configs/opencua.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/configs/uitars1.5-7B.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/env_setup/hydrate.py` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/environments/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/environments/cli_workspace_environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/environments/screenenv_environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/unittests/test_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/ppteval/unittests/test_environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/ppteval/environments/cli_workspace_environment.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/ppteval/run_benchmark.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
