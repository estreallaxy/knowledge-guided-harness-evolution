# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/vigil/config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/vigil/goal_completion_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/path_cache.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/enhanced_tools_loop.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/tool_sanitizer_element.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/vigil_executor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/runtime_auditor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/enhanced_executor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/config.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/types.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vigil/conditional_llm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
