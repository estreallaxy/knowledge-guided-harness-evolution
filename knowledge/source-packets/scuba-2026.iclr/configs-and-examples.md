# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE.txt` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agents/anthropic/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/browser_use/custom/evaluators/vwa/env_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/envs/remote_docker_env/readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/how_to_license.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements_bu.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements_cu.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements_ray_opencua.txt` | Dependency, configuration, or usage evidence. |
| `official-code/scuba/prerequisites/metadata/fields/Environment__c.Age__c.field-meta.xml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agents/anthropic/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/anthropic/tools/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/s2_5/cli_app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scuba/phases/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
