# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/examples/test_qwen3.py` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/megabench/metrics/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/ok_vqa/_generate_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/refcocog/_generate_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/vizwiz_vqa/_generate_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/lmms-eval/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/math/evaluation/examples.py` | Dependency, configuration, or usage evidence. |
| `official-code/experiments/math/evaluation/latex2sympy/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/experiments/longmemeval/src/evaluation/evaluate_qa.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/longmemeval/src/retrieval/eval_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiments/longmemeval/src/retrieval/run_retrieval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
