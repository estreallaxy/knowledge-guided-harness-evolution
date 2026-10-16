# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/browsergym/stwebagentbench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/browsergym/stwebagentbench/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/browsergym/stwebagentbench/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/browsergym/stwebagentbench/src/browsergym/stwebagentbench/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/test_setup_scripts_browser.py` | Dependency, configuration, or usage evidence. |
| `official-code/st_bench_example.py` | Dependency, configuration, or usage evidence. |
| `official-code/st_bench_example_loop.py` | Dependency, configuration, or usage evidence. |
| `official-code/stwebagentbench/browser_env/env_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/stwebagentbench/llms/lm_config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/stwebagentbench/test_eval/test_benchmark_validation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stwebagentbench/test_eval/test_evaluator_comb.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stwebagentbench/test_eval/test_url_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stwebagentbench/test_eval/test_string_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stwebagentbench/test_eval/test_html_content_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stwebagentbench/test_eval/test_action_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stwebagentbench/test_eval/test_content_validation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stwebagentbench/evaluation_harness/evaluators.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
