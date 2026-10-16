# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval/lmms_eval/tasks/ok_vqa/_generate_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval/tools/live_bench/live_bench/data_generator/example/example_output.json` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval/tools/live_bench/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval/tools/live_bench/script/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/lmms-eval/tools/live_bench/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/visual_head/LLaVA-NeXT/trl/environment/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/visual_head/LLaVA-NeXT/trl/environment/base_environment.py` | Dependency, configuration, or usage evidence. |
| `official-code/visual_head/LLaVA-NeXT/trl/trainer/reward_config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/lmms-eval/tools/live_bench/live_bench/data_generator/score_getter.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/get_final_scores.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/req_score.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/f1_score.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/result_summary.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval/tools/get_video_avg_time.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval/tools/regression.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/lmms-eval/tools/lite/embed.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
