# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config.kv.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/config.text.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/config_utils.py` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/hotpotqa/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/hotpotqa/config.kv.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/hotpotqa/config.text.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/locomo/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/locomo/config.text.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/examples/quickstart.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/config/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/config/schema.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_config_module.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_config_schema.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/memory/router/bm25_scorer.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/memory/memory_agent/text_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/memory/router/embedding_factory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/memory/router/router.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/memory/router/hybrid_router.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/memory/memory_agent/agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_memory_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_memory_agent_extended.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
