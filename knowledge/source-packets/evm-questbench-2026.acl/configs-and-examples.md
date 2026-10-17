# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README_CN.md` | Dependency, configuration, or usage evidence. |
| `official-code/bsc_quest_bench/check_setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/bsc_quest_bench/example_usage.py` | Dependency, configuration, or usage evidence. |
| `official-code/bsc_quest_bench/skill_runner/tsconfig.json` | Dependency, configuration, or usage evidence. |
| `official-code/bsc_quest_bench/system_config.json` | Dependency, configuration, or usage evidence. |
| `official-code/bsc_quest_bench/system_config_viem.json` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/run_quest_bench.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
