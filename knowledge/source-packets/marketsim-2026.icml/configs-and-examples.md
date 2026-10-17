# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/ExampleExperimentalAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/ExampleLLMagent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/ImpactAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/MarketReplayAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/MomentumAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/QLearningAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/ShockAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/SubscriptionAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/SumClientAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/SumServiceAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/crypto/PPFL_ClientAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/crypto/PPFL_ServiceAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent/examples/crypto/PPFL_TemplateClientAgent.py` | Dependency, configuration, or usage evidence. |
| `official-code/config/exp_agent_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/config_LLM.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agent/examples/SumServiceAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/SubscriptionAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/SumClientAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/MomentumAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/MarketReplayAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/ExampleExperimentalAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/ImpactAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/ShockAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/QLearningAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/ExampleLLMagent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/crypto/PPFL_ServiceAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/examples/crypto/PPFL_TemplateClientAgent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
