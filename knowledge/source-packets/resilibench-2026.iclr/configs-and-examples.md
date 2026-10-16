# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tool_registry_realAPI.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tool_registry.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/README.md` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/task_library_realAPI.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/simulated_tasks_enhanced/task_library_enhanced_v3_very_hard_with_workflows.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/simulated_tasks_enhanced/task_library_enhanced_v3_very_easy_with_workflows.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/simulated_tasks_enhanced/task_library_enhanced_v3_medium_with_workflows.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/simulated_tasks_enhanced/task_library_enhanced_v3_medium_biased_with_workflows.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/simulated_tasks_enhanced/task_library_enhanced_v3_hard_with_workflows.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/simulated_tasks_enhanced/task_library_enhanced_v3_hard_biased_with_workflows.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/simulated_tasks_enhanced/task_library_enhanced_v3_easy_with_workflows.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/simulated_tasks_enhanced/task_library_enhanced_v3_easy_biased_with_workflows.json` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
