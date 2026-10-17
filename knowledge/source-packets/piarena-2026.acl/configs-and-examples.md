# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/agents/InjecAgent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/attack.py` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/counter_benchmark/benchmark.py` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/counter_benchmark/suites/counter/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/counter_benchmark/suites/counter/injection_tasks.py` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/counter_benchmark/suites/counter/task_suite.py` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/counter_benchmark/suites/counter/user_tasks.py` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/counter_benchmark/suites/tools.py` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/functions_runtime.py` | Dependency, configuration, or usage evidence. |
| `official-code/agents/agentdojo/examples/pipeline.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agents/InjecAgent/src/evaluate_finetuned_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/InjecAgent/src/evaluate_prompted_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
