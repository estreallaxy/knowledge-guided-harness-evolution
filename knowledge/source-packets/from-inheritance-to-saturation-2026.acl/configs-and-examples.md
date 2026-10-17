# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.35v/lmms_eval/tasks/megabench/metrics/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.35v/tools/live_bench/live_bench/data_generator/example/example_output.json` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.35v/tools/live_bench/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.35v/tools/live_bench/script/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.35v/tools/live_bench/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/megabench/metrics/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.5v/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.5v/tools/live_bench/live_bench/data_generator/example/example_output.json` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.5v/tools/live_bench/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.5v/tools/live_bench/script/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval-0.5v/tools/live_bench/setup.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/lmms-eval-0.5v/tools/live_bench/live_bench/data_generator/score_getter.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.35v/tools/live_bench/live_bench/data_generator/score_getter.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/ocrbench_v2/IoUscore_metric.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/mmsearch/get_final_scores.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.35v/lmms_eval/tasks/mmsearch/get_final_scores.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/mmsearch/score/req_score.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.35v/lmms_eval/tasks/mmsearch/score/req_score.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/gedit_bench/viescore/parse_prompt.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/mmsearch/score/f1_score.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval-0.35v/lmms_eval/tasks/mmsearch/score/f1_score.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
