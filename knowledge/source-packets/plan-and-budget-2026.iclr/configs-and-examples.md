# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/utils/prompt_list.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/utils/data.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/inference/_0_vanilla_model.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/inference/_2_global_budget_model.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/inference/_1_planned_model.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/inference/_3_planned_global_model.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/inference/_4_planned_local_uniform_model.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/utils/logger.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/inference/_5_planned_local_weighted_model.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/utils/math.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/utils/utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
