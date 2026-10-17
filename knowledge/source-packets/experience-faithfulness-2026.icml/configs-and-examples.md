# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/ExpeL/configs/agent/expel.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ExpeL/configs/benchmark/alfworld.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ExpeL/configs/benchmark/fever.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ExpeL/configs/benchmark/hotpotqa.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ExpeL/configs/benchmark/webshop.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ExpeL/configs/eval.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ExpeL/configs/insight_extraction.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/ExpeL/configs/visualize_logs.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/ReasoningBank/autoeval/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/cdt/src/faiss_attn/source/configuration_qwen3.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/ReasoningBank/autoeval/evaluate_trajectory.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/ReasoningBank/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/ReasoningBank/scripts/run_gitlab.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/ReasoningBank/scripts/run_map.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/ReasoningBank/scripts/run_reddit.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cdt/src/scripts/run_14B.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cdt/src/scripts/run_32B.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cdt/src/scripts/run_8B.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
