# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/config/settings.py` | Dependency, configuration, or usage evidence. |
| `official-code/env/alfworld/simple_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/examples/alfworld_essa_run.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/alfworld_react_run.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/task_lists/alfworld/alfworld_valid_seen_full.txt` | Dependency, configuration, or usage evidence. |
| `official-code/examples/task_lists/alfworld/alfworld_valid_unseen_full.txt` | Dependency, configuration, or usage evidence. |
| `official-code/examples/task_lists/alfworld/alfworld_valid_unseen_heat_then_place_in_recep.txt` | Dependency, configuration, or usage evidence. |
| `official-code/examples/task_lists/alfworld/alfworld_valid_unseen_look_at_obj_in_light.txt` | Dependency, configuration, or usage evidence. |
| `official-code/examples/task_lists/alfworld/alfworld_valid_unseen_pick_and_place.txt` | Dependency, configuration, or usage evidence. |
| `official-code/examples/task_lists/alfworld/alfworld_valid_unseen_pick_clean_then_place_in_recep.txt` | Dependency, configuration, or usage evidence. |
| `official-code/examples/task_lists/alfworld/alfworld_valid_unseen_pick_two_obj_and_place.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agent/ReactAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/ESSAAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/prompt/ReactAgent_prompt.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/prompt/ESSA_prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/offline_induction/prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/config/settings.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/alfworld_react_run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
