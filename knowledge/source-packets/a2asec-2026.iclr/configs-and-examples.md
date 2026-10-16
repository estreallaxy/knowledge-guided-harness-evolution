# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/llm/co_eval.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/offline/atsi_eval.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/offline/co_eval.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/offline/hotf_eval.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_asrf_executable_environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_atsi_executable_environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_co_executable_environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_hotf_executable_environment.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tests/test_hotf_executable_environment.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_atsi_executable_environment.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_co_executable_environment.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_asrf_executable_environment.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/orchestration.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_agentcard_io.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/test_a2a_attack_behavior.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
