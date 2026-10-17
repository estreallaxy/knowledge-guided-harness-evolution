# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/OmniSimpleMem/examples/multimodal_memory.py` | Dependency, configuration, or usage evidence. |
| `official-code/OmniSimpleMem/omni_memory/core/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/OmniSimpleMem/omni_memory/evolution/evolution_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/OmniSimpleMem/omni_memory/utils/logging_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/docker-compose.yml` | Dependency, configuration, or usage evidence. |
| `official-code/examples/quickstart.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements-gpu.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/simplemem/core/config_default.py` | Dependency, configuration, or usage evidence. |
| `official-code/simplemem/multimodal/core/config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/OmniSimpleMem/omni_memory/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
