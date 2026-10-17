# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/claude_ablations/claude4-5-fast-memory.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/claude_ablations/claude4-6-fast-memory.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/default.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/default_base_llm.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/long_run/memoryless.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/long_run/no_websearch.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/prover_v2_qwen.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/tools.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/gcp/docker/upload_artifacts.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/src/ax_prover/commands/configure.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/ax_prover/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/ax_prover/configs/default.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/src/ax_prover/configs/llms.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/src/ax_prover/configs/tools.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/src/ax_prover/utils/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/unit/utils/test_config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/ax_prover/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
