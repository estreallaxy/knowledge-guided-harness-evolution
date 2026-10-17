# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/examples/minimal_input_model.json` | Dependency, configuration, or usage evidence. |
| `official-code/docs/installation.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/quickstart.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/src/dsbx/Agents/LLMCoder/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/dsbx/Agents/LLMScheduler/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/dsbx/Agents/RACEC/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/dsbx/Gen/io/config_migrator.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/dsbx/Agents/CLI.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/dsbx/Eval/CLI.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
