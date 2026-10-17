# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/gorilla/agent-arena/client/src/setupTests.js` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/domains/airline/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/domains/mock/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/domains/retail/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/domains/telecom/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/environment/db.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/environment/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/environment/server.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/environment/tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/environment/toolkit.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/environment/utils/interface_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/tau2-bench/src/tau2/orchestrator/environment_manager.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tau2-bench/src/tau2/scripts/evaluate_trajectories.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
