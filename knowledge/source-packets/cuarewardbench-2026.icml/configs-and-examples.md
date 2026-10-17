# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/models.example.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/prompts/osworld_opencua_reflect_thinking.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/prompts/osworld_sewsm_thinking.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/prompts/osworld_zerogui.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/voting.example.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/cuarewardbench/core/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/cuarewardbench/core/model_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/cuarewardbench/cli/eval_benchmark.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cuarewardbench/cli/eval_trajectory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/run_eval_cuarewardbench.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/run_eval_trajectories.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
