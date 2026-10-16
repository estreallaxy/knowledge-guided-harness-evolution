# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/best_agent/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/best_agent/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/best_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/polyglot/docker_build.py` | Dependency, configuration, or usage evidence. |
| `official-code/polyglot/docker_utils.py` | Dependency, configuration, or usage evidence. |
| `official-code/polyglot/dockerfiles.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/utils/docker_utils.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/best_agent/utils/eval_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluate_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/polyglot/run_evaluation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/utils/eval_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
