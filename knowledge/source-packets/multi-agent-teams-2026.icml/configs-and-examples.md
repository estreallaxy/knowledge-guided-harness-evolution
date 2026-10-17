# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/configs/gpqa_diamond.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/configs/hle_text_only.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/configs/lost_at_sea.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/configs/math_500.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/configs/mmlu_pro.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/configs/moon_survival.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/configs/simpleqa.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/configs/student_body_president.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/experiments/run_gpqa_diamond.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_hle_text_only.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_lost_at_sea.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_math_500.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_mmlu_pro.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_moon_survival.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_simpleqa.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/run_student_body_president.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
