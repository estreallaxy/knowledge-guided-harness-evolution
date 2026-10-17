# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/case_studies/code_agent/code_agent_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/case_studies/code_agent/readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/case_studies/computer_use_agent/computer_use_agent_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/case_studies/computer_use_agent/readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/case_studies/embodied_agent/embodied_agent_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/case_studies/embodied_agent/readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/case_studies/embodied_agent/sandbox_root/environment_state.py` | Dependency, configuration, or usage evidence. |
| `official-code/case_studies/embodied_agent/sandbox_root/scene_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/readme.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/case_studies/embodied_agent/sandbox_root/environment_state.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/state.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent_factory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tools.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tool_wrapper.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/case_studies/embodied_agent/embodied_agent_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/case_studies/code_agent/code_agent_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
