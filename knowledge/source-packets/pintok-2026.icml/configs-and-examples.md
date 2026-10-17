# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/setup_dpdk.sh` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/docker-compose.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/llm_service.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/main.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/models.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/rag_workflow.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/start.sh` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/test_app.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/test_components.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/utils.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/agentic_app/vector_store.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/example_chromadb.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/examples/example_pgvector.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/python/setup.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/python/examples/agentic_app/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
