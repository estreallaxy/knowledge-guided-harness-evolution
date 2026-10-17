# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/arithmetic/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/arithmetic/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/arithmetic/task.py` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/arithmetic/task_with_rubric.py` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/arithmetic/task_with_tools.py` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/code_execution/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/code_execution/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/code_execution/compose.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/demo/code_execution/task.py` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/labbench/litqa2/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/paper_finder/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/evals/super/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/astabench/tools/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/setup.cfg` | Dependency, configuration, or usage evidence. |
| `official-code/solvers/scorer/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/scripts/eval_then_score.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/solvers/scorer/demo.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
