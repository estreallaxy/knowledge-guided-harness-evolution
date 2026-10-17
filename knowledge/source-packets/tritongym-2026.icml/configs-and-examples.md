# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/web/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/web/backend/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/benchmark/agents/base.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/oneshot_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/alphaevolve_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/geak_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/leader_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/clients/base.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/clients/meta_client.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/clients/anthropic_client.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/clients/deepseek_client.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/data_v2/tests/attention_score.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/clients/openai_client.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/agents/clients/google_client.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
