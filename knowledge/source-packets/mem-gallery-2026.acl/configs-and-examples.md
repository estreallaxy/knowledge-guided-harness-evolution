# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultAUGUSTUSMemoryConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultEvalConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultFunctionConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultGlobalConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultMMFUMemoryConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultMMMemoryConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultMemoryConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultNGMemoryConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultOperationConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultUniversalRAGMemoryConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/default_config/DefaultUtilsConfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/memengine/config/Config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/benchmark/memengine/memory/FUMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/STMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/LTMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/BaseMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/RFMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/MMFUMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/MMMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/NGMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/GAMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/UniversalRAGMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/MGMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/memengine/memory/AUGUSTUSMemory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
