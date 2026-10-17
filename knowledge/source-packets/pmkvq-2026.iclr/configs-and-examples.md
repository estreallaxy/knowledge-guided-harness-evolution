# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/demo_pm_kvq.py` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/pm_kvq/evaluation/eval_aime.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/pm_kvq/evaluation/eval_cmimc.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/pm_kvq/evaluation/eval_livecodebench/eval_livecodebench.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/pm_kvq/evaluation/eval_wrapper.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/demo_pm_kvq.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
