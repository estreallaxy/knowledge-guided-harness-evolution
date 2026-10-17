# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/roga/ablation_configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/roga/init_tools/configs.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/roga/prompt/tool_validator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/prompt/tool_wrapper.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/prompt/tool_generator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/tool/tool_searcher.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/prompt/planner.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/core/assistant.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/core/sandbox.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/core/session.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/init_tools/call_llm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/tool/tool_wrapper.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/init_tools/get_table_metadata.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/roga/init_tools/table2md.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
