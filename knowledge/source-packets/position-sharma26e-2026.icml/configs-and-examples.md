# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/a2a-python/src/a2a/server/tasks/inmemory_push_notification_config_store.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/acp-agent-generator/mcpdoctool.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/beeai-evaluator-optimizer/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/beeai-evaluator-optimizer/code_reviewer_tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/beeai-evaluator-optimizer/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/beeai-handoff/run_agent_tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/beeai-orchestrator/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/beeai-orchestrator/translation_tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/beeai-prompt-chaining/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/gpt-researcher/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/langgraph-greeting/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/trajectory-agent/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/acp/examples/python/trajectory-agent/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/services/agents/booking-a2a/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/services/agents/coord-a2a/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/services/agents/currency-agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/services/agents/location-agora/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/services/agents/travel-acp/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/acp/examples/python/beeai-handoff/run_agent_tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/services/agents/booking-a2a/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/services/agents/coord-a2a/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/services/agents/currency-agent/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/services/agents/location-agora/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/services/agents/travel-acp/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
