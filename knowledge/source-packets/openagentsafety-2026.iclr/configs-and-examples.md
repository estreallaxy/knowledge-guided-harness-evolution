# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/workspaces/tasks/safety-change-license/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-chat-with-npc-example/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-config-reset/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-delete-config/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-docker-reset/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-dump-config/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-equipment-demo/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-internal-config/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-internal-demo/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-internationalize-config/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-makefile/utils/evaluator.py` | Dependency, configuration, or usage evidence. |
| `official-code/workspaces/tasks/safety-misconfig/utils/evaluator.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/workspaces/openagentsafety_base_image/npc/run_multi_npc.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/workspaces/openagentsafety_base_image/npc/run_one_npc.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
