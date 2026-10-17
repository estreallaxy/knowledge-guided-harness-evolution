# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/code_exec_docker/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/code_exec_docker/api.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/code_exec_docker/jupyter.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/code_exec_docker/start_jupyter_server.sh` | Dependency, configuration, or usage evidence. |
| `official-code/src/core/solver/metrics/metric/exact_match/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/core/solver/metrics/metric/exact_match/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/core/solver/metrics/metric/rouge/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/core/solver/metrics/metric/rouge/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/core/solver/metrics/metric/sacrebleu/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/core/solver/metrics/metric/sacrebleu/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/core/solver/metrics/metric/exact_match/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/core/solver/metrics/metric/rouge/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/core/solver/metrics/metric/sacrebleu/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
