# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/claude_code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/claude_code/batch_run_docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/claude_code/run_docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/claude_code/setup-env.sh` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/gemini_cli/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/gemini_cli/batch_run_docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/gemini_cli/run_docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/gemini_cli/setup-env.sh` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/openhands/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_harness/swe_agent/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/susvibes/curate/env_setup/dev_tools.py` | Dependency, configuration, or usage evidence. |
| `official-code/susvibes/curate/env_setup/prompts.py` | Dependency, configuration, or usage evidence. |
| `official-code/susvibes/curate/test/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/susvibes/curate/utils/agents/configs/curate.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/susvibes/curate/utils/agents/configs/env_setup.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/susvibes/curate/utils/agents/configs/test_gen.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/evaluation_harness/claude_code/run_docker.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation_harness/gemini_cli/run_docker.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation_harness/swe_agent/run_infer.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
