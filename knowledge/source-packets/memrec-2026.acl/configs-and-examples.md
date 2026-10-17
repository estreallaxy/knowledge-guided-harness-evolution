# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/common.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/memrec_agent_instructrec-books.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/memrec_instructrec-books.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/memrec_instructrec-books_1k.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/memrec_instructrec-goodreads.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/memrec_instructrec-movietv.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/memrec_instructrec-yelp.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/env/environment.yml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/setup_env.sh` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/update_config_with_user_list.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
