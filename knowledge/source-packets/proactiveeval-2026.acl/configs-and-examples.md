# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/dataset_generation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/dataset_generation/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/dataset_generation/examples/environment_generation_examples.json` | Dependency, configuration, or usage evidence. |
| `official-code/dataset_generation/examples/evaluation_test_examples.json` | Dependency, configuration, or usage evidence. |
| `official-code/dataset_generation/examples/trigger_factor_add_noises_examples.json` | Dependency, configuration, or usage evidence. |
| `official-code/dataset_generation/examples/trigger_factor_rewrite_examples.json` | Dependency, configuration, or usage evidence. |
| `official-code/dataset_generation/examples/user_information_add_noises_examples.json` | Dependency, configuration, or usage evidence. |
| `official-code/dataset_generation/examples/user_information_rewrite_examples.json` | Dependency, configuration, or usage evidence. |
| `official-code/eval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/eval/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/eval/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/eval/prompt/target_planning_eval_examples.py` | Dependency, configuration, or usage evidence. |
| `official-code/readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/eval/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
