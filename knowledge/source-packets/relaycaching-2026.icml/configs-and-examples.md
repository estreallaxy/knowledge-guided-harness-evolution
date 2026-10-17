# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/RelayCaching/llm/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/datasets_self/MMLU/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/experiments/main/run_gsm8k.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/main/run_humaneval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/main/run_mmlu.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/observation/run_observation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/profiler/run_layer_profiler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
