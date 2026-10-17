# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/scope/prompt/example_data.json` | Dependency, configuration, or usage evidence. |
| `official-code/scope/prompt/prompt_scope_travel_planner/example_solution.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/baselines/run_directreasoning_natural_plan.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/baselines/run_directreasoning_travel_planner.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluate_meeting_planning.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluate_trip_planning.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_scope_natural_plan.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_scope_travel_planner.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
