# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/sweagent/environment/hooks/abstract.py` | Dependency, configuration, or usage evidence. |
| `official-code/sweagent/environment/hooks/status.py` | Dependency, configuration, or usage evidence. |
| `official-code/sweagent/environment/repo.py` | Dependency, configuration, or usage evidence. |
| `official-code/sweagent/environment/swe_env.py` | Dependency, configuration, or usage evidence. |
| `official-code/tool_gen/evaluation/setup_scripts/make_eval_dir_from_selected_subagents.py` | Dependency, configuration, or usage evidence. |
| `official-code/tools/diff_state/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/tools/filemap/install.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/multilingual_setup/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/tools/multilingual_setup/install.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/registry/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/tools/search/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/tools/search/install.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/subagent/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/tools/submit/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/tools/submit_subagent/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/tools/windowed_edit_linting/install.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/windowed_edit_replace/install.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/windowed_edit_rewrite/install.sh` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tool_gen/main_agent_generator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
