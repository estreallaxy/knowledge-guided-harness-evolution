# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/ablation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/petri/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/toolbox_expansion/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/toolbox_expansion/auditor_tool_setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/usc_config.json` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/baselines/petri/evaluate_petri_trajectories.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation_judges/evaluate_catastrophic_impact.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation_judges/evaluate_cli_behavior.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation_judges/evaluate_cli_traj.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation_judges/evaluate_extra_mile.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/trajectory_generation/run_claude_code.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/trajectory_generation/run_gemini_cli_phase1.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/trajectory_generation/run_gemini_cli_phase2.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
