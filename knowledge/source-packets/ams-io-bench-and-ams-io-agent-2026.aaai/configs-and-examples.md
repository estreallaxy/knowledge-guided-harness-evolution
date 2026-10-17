# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/agent_generated/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/app/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/app/intent_graph/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/app/layout/process_node_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/app/schematic/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/app/utils/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/app/utils/config_utils.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/scripts/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/scripts/devices/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/scripts/ramic_bridge/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/skill/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/tools/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/tools/example_search_tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/tools/python_helpers/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/tools/tools_config.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/tools/example_search_tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agent_generated/fibonacci_sequence.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agent_generated/read_skill_file.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agent_generated/save_json_file.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agent_generated/create_text_file.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/agent_generated/save_json_with_directory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/tool_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/user_profile_tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/task_query_tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/tool_stats_tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
