# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README_zh.md` | Dependency, configuration, or usage evidence. |
| `official-code/code/utils/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/code/evaluation/evaluation_probability_calculation_human.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/code/evaluation/evaluation_probability_calculation_human_preprocess.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/code/evaluation/evaluation_probability_calculation_human_preprocess_factcheck.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/code/evaluation/evaluation_probability_calculation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/code/utils/utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/code/baselines/model_direct.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/code/baselines/model_probability_direct.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/code/baselines/model_probability_compare.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
