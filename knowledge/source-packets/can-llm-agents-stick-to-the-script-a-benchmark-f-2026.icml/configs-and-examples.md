# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README.zh-CN.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/reference-methods/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/reference-methods/baseline/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/reference-methods/hiagent/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/reference-methods/hiagent/src/ncpbench_reference_hiagent/config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/ncpbench/evaluator_prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/reference-methods/hiagent/src/ncpbench_reference_hiagent/hiagent_prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/reference-methods/hiagent/src/ncpbench_reference_hiagent/config.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/ncpbench/metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/ncpbench/evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_evaluator_protocol.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
