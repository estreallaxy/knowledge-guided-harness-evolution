# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/packages/autolibra-core/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/packages/autolibra-core/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/packages/autolibra-core/src/autolibra_core/configs/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/packages/osw-data/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/prompt_optimization/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/src/training/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/packages/osw-data/src/osw_data/metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/packages/autolibra-core/src/autolibra_core/evaluators/llm_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/packages/autolibra-core/src/autolibra_core/evaluators/coverage_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/training/prompt_improver_direct_data.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/packages/osw-data/tests/test_metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/packages/osw-data/src/osw_data/trajectory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/packages/autolibra-core/src/autolibra_core/configs/__init__.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
