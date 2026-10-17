# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.agents/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/gamedevbench/src/utils/prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/gamedevbench/src/benchmark_runner.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/gamedevbench/src/utils/validation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/gamedevbench/src/utils/merge_benchmark_results.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/validate_tasks.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_merge_benchmark_results.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_benchmark_resume.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/gamedevbench/src/virtual_display.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
