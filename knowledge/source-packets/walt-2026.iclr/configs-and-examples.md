# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/src/walt/benchmarks/vwa/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/benchmarks/vwa/accounts_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/benchmarks/vwa/generate_test_configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/benchmarks/wa/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/benchmarks/wa/accounts_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/benchmarks/wa/generate_test_configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/browser_use/custom/evaluators/vwa/env_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/browser_use/custom/evaluators/wa/env_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/tools/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/tools/demonstrator/service.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/walt/tools/demonstrator/views.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/walt/tools/discovery/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
