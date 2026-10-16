# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/quickstart/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/quickstart/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/quickstart/embedder.py` | Dependency, configuration, or usage evidence. |
| `official-code/quickstart/llm_client.py` | Dependency, configuration, or usage evidence. |
| `official-code/quickstart/memory.py` | Dependency, configuration, or usage evidence. |
| `official-code/quickstart/retriever.py` | Dependency, configuration, or usage evidence. |
| `official-code/quickstart/schemas.py` | Dependency, configuration, or usage evidence. |
| `official-code/quickstart/store.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/evaluation/eval_query_type.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/retrieval/eval_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/retrieval/run_retrieval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
