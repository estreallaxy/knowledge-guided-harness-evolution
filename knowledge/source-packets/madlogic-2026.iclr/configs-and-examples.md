# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/agentverse/environments/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/basic.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/llm_eval.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/describer/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/describer/basic.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/order/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/order/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/order/concurrent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/selector/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/updater/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/updater/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/updater/basic.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/visibility/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/visibility/all.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentverse/environments/rules/visibility/base.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/run_evaluation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
