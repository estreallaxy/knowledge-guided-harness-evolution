# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/maintainers/post_verify/prune-config-authoring.md` | Dependency, configuration, or usage evidence. |
| `official-code/harness/e2e/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/harness/e2e/container_setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/harness/e2e/repo_config_binding.py` | Dependency, configuration, or usage evidence. |
| `official-code/harness/prepare_repo/split_test_patches/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/harness/test_runner/core/docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/tests/e2e/test_container_setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/e2e/test_repo_config_binding.py` | Dependency, configuration, or usage evidence. |
| `official-code/trial_config.example.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/harness/test_runner/core/test_executor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/harness/test_runner/core/docker.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/e2e/test_agent_prompt.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/e2e/test_tool_search_setting.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/e2e/test_evaluator_compile_fail_closed.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/e2e/test_evaluator_filter.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/e2e/test_rescore_filter_only.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
