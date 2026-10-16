# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/agentdojo/functions_runtime.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agentdojo/attacks/attack_registry.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agentdojo/agent_pipeline/planner.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agentdojo/attacks/dos_attacks.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agentdojo/attacks/important_instructions_attacks.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agentdojo/attacks/base_attacks.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agentdojo/agent_pipeline/tool_execution.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
