# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README_CN.md` | Dependency, configuration, or usage evidence. |
| `official-code/docker_images.txt` | Dependency, configuration, or usage evidence. |
| `official-code/launch/launch/agent/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/launch/launch/utilities/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/pull_docker.sh` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/docker_build.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/docker_utils.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/c.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/go.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/java.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/javascript.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/php.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/python.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/ruby.py` | Dependency, configuration, or usage evidence. |
| `official-code/swebench/harness/dockerfiles/rust.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/swebench/harness/modal_eval/run_evaluation_modal_entrypoint.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/swebench/harness/run_evaluation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/swebench/harness/run_validation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/swecompass/evaluators/configuration_deployment/eval_executor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/swecompass/evaluators/performance_optimization/eval_executor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/swecompass/evaluators/selected/eval_executor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
