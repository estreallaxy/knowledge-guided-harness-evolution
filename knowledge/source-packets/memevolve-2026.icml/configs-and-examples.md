# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Flash-Searcher-main/mini-swe-agent/docs/reference/environments/docker.md` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/docs/reference/environments/swerex_docker.md` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/config/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/config/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/extra/bubblewrap.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/extra/swerex_docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/local.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/src/minisweagent/environments/singularity.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/extra/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/extra/test_bubblewrap.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/extra/test_swerex_docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/test_docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/test_init.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/test_local.py` | Dependency, configuration, or usage evidence. |
| `official-code/Flash-Searcher-main/mini-swe-agent/tests/environments/test_singularity.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/Flash-Searcher-main/eval_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
