# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/6_component_evaluation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/6_component_evaluation/alpaca_eval_gpt4_turbo_fn/configs.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/6_component_evaluation/alpaca_eval_gpt4_turbo_fn/modified_configs.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/dataset_info.json` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference_example.py` | Dependency, configuration, or usage evidence. |
| `official-code/full_paper_evaluation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/examples/async_batch.py` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/examples/basic_usage.py` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/examples/different_judges.py` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/examples/reproduce_xtragpt.py` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/examples/reproduce_xtragpt_correct.py` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/examples/reproduce_xtragpt_final.py` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/examples/reproduction_results.json` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/examples/sample_data.json` | Dependency, configuration, or usage evidence. |
| `official-code/paper_revision_bench/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/tests/openclaw-demo/demo_script.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tests/openclaw-demo/extract_paper.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/6_component_evaluation/run_eval.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/paper_revision_bench/paper_revision_bench/cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/openclaw-demo/demo_script.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/openclaw-demo/run_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
