# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/setup_alert_only.sh` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/setup_docker.sh` | Dependency, configuration, or usage evidence. |
| `official-code/secgym/agents/expel_train/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/secgym/agents/react_examples/react_example_1.txt` | Dependency, configuration, or usage evidence. |
| `official-code/secgym/agents/react_examples/react_example_2.txt` | Dependency, configuration, or usage evidence. |
| `official-code/secgym/agents/react_examples/react_example_3.txt` | Dependency, configuration, or usage evidence. |
| `official-code/secgym/database/setup_database.py` | Dependency, configuration, or usage evidence. |
| `official-code/secgym/myconfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/secgym/agents/prompt_sauce_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/prompt_sauce_reflexion_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/setup.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/agent_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/expel_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/maset_slave_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/react_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/react_reflexion_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/baseline_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/expel_train/experience_recall.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/secgym/agents/expel_train/insight_extraction.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
