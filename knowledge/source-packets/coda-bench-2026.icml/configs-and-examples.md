# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/coda_bench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/docker/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/docker/build_all.sh` | Dependency, configuration, or usage evidence. |
| `official-code/docker/openhands/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/docker/openhands/entrypoint.sh` | Dependency, configuration, or usage evidence. |
| `official-code/docker/openhands/network-lock.sh` | Dependency, configuration, or usage evidence. |
| `official-code/docker/openhands/openhands-sdk.py` | Dependency, configuration, or usage evidence. |
| `official-code/docker/openhands/run_task.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/evaluate_predictions.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/load_dataset.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/setup_dataset.py` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/test_installation.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_dataset_setup.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/coda_bench/cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/docker/openhands/run_task.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/evaluate_predictions.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/run_evaluation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
