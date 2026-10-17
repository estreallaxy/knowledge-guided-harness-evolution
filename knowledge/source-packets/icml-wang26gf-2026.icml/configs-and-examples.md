# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/experiment_config.json` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/minimal_counterexample.py` | Dependency, configuration, or usage evidence. |
| `official-code/python_harness/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/experiments/run_all_neurips_defense.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_defense_local_sweep.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_temporal_local_models.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_temporal_new_models.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/python_harness/src/pse_harness/cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_experiments.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
