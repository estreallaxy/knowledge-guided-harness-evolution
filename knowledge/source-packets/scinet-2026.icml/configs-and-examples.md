# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/readme.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/Evaluation/task1-novelty-rank.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/Evaluation/task1-disruption-rank.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/Evaluation/task1-disruptive-sos.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/Evaluation/task3-path-connectivity.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/Evaluation/task1-novelty-sos.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/Evaluation/task1-novelty-llm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/Evaluation/task1-disruptive-llm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
