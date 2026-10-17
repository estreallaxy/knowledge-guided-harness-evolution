# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/exp3/categorization/language-matters/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/related_work/protegi/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/related_work/protegi/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/lib/eval/ds1000/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/lib/eval/ds1000/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/lib/eval/ds1000/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/lib/eval/truthfulqa/configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/lib/ifeval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/lib/ifeval/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/scripts/lib/eval/alpaca_farm/run_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/lib/eval/codex_humaneval/run_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/lib/eval/ds1000/run_inference.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/lib/eval/ds1000/run_test.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/lib/eval/gsm/run_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/lib/eval/toxigen/run_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/lib/eval/triviaqa/run_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/lib/eval/truthfulqa/run_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/reward_modeling/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/reward_modeling/main_multi_metric.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/reward_modeling/main_multi_metric_one.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
