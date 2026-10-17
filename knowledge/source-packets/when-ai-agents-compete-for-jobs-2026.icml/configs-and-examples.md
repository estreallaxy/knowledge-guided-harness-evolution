# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/ablation.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/ablation_old.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/baseline.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/baseline_old.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/market_change.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/market_change_open_bid.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/market_recession.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/moral.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/price.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/ssa/experiment_config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/ssa/run_experiment.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
