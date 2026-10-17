# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/agentmark/environments/alfworld/action_executor.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentmark/environments/alfworld/alfworld_3prompts.json` | Dependency, configuration, or usage evidence. |
| `official-code/agentmark/environments/alfworld/prompt.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentmark/environments/toolbench/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentmark/environments/toolbench/adapter.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentmark/environments/toolbench/data_loader.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentmark/environments/toolbench/fake_response.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentmark/environments/toolbench/output.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentmark/environments/toolbench/prompt.py` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/toolbench/tools/stable_toolbench_eval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/toolbench/tools/stable_toolbench_eval/evaluators/tooleval_gpt-3.5-turbo_default/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/toolbench/tools/stable_toolbench_eval/evaluators/tooleval_gpt-3.5-turbo_fn/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/toolbench/tools/stable_toolbench_eval/evaluators/tooleval_gpt-3.5-turbo_normalized/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/toolbench/tools/stable_toolbench_eval/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/experiments/oasis_watermark/reddit_watermark_experiment/evaluate_metrics_llm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/oasis_watermark/twitter_watermark_experiment/evaluate_metrics_llm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/toolbench/scripts/run_experiment.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/toolbench/scripts/run_massive_parallel.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/toolbench/scripts/run_pipeline.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
