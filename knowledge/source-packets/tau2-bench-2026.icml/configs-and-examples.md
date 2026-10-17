# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/examples/agents/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/examples/agents/custom_agent_eval.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/agents/minimal_text_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/agents/react_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/agent/base/llm_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/domains/airline/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/domains/banking_knowledge/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/domains/mock/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/domains/retail/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/domains/telecom/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/environment/db.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/environment/environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/environment/server.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/environment/tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/environment/toolkit.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/environment/utils/interface_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tau2/orchestrator/environment_manager.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/experiments/agentify_tau_bench/src/agentify_tau_bench/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tau2/scripts/evaluate_trajectories.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
