# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/doc/docker_installation.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/run_example.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/robomme/env_record_wrapper/DemonstrationWrapper.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/robomme/env_record_wrapper/EndeffectorDemonstrationWrapper.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/robomme/env_record_wrapper/MultiStepDemonstrationWrapper.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/robomme/env_record_wrapper/OraclePlannerDemonstrationWrapper.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/robomme/env_record_wrapper/episode_config_resolver.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/scripts/run_example.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
