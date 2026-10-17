# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README_zh.md` | Dependency, configuration, or usage evidence. |
| `official-code/config/new_prompts.py` | Dependency, configuration, or usage evidence. |
| `official-code/l0_memory/embedding_interface/base_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/l0_memory/llm_interface/base_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/l1_memory/configs/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/l1_memory/configs/embeddings/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/l1_memory/configs/llms/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/l1_memory/embeddings/configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/l1_memory/graphs/configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/l1_memory/llms/configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/l1_memory/memory/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/l1_memory/memory/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/evaluate_l0_plus_l1.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
