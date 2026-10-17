# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/clusters/Ballast_Configuration_Cluster.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/clusters/Boolean_State_Configuration_Cluster.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/clusters/Pump_Configuration_and_Control_Cluster.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/clusters/Thermostat_User_Interface_Configuration_Cluster.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/clusters/Valve_Configuration_and_Control_Cluster.md` | Dependency, configuration, or usage evidence. |
| `official-code/eval_spec.example.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/gen_spec.example.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/src/cli/config_resolver.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/pipelines/episode_generation/core/home_config_initializer.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/agents/tools.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agents/memory/hi_memory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/cli/episode_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agents/types.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agents/__init__.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agents/strategies/__init__.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agents/providers/base.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agents/strategies/base.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agents/providers/openai_provider.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
