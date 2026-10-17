# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/dataset_construction/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/environment_opencompass.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/eval/FB-Bench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/eval/FB-Bench/config/api_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/eval/FB-Bench/config/gen_answer_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/eval/FB-Bench/config/judge_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/eval/FB-Bench/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/eval/WildBench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/eval/WildBench/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/eval/opencompass/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/eval/opencompass/configs/eval_subjective_mtbench101_myagent.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements_vllm_stable.txt` | Dependency, configuration, or usage evidence. |
| `official-code/web-deploy/BENCHMARK_README.md` | Dependency, configuration, or usage evidence. |
| `official-code/web-deploy/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/web-deploy/backend/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/web-deploy/benchmark_requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/web-deploy/ievo-study/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/web-deploy/ievo-study/eslint.config.js` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/eval/WildBench/run_agent.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/eval/opencompass/configs/eval_subjective_mtbench101_myagent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
