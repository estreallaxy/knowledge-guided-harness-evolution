# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/benchmarks/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/benchmarks/infinite_bench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/benchmarks/longbench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/benchmarks/longbenchv2/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/benchmarks/loogle/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/benchmarks/ruler/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/benchmarks/zero_scrolls/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/evaluate_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/notebooks/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/evaluation/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/evaluate_registry.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
