# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirement.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/config/check_model.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/src/config/reasoning_model.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/src/scripts/config.sh` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/scripts/run_base.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/scripts/run_build_index_bm25.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/scripts/run_build_index_embedding.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/scripts/run_check_think_offline.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/scripts/run_check_think_online.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/scripts/run_vanilla.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
