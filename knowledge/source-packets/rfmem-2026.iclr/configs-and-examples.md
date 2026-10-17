# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/RF_mem/LongMemEval/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/RF_mem/LongMemEval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/RF_mem/LongMemEval/requirements-full.txt` | Dependency, configuration, or usage evidence. |
| `official-code/RF_mem/LongMemEval/requirements-lite.txt` | Dependency, configuration, or usage evidence. |
| `official-code/RF_mem/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/RF_mem/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/RF_mem/LongMemEval/run.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/LongMemEval/src/evaluation/evaluate_qa.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/LongMemEval/src/generation/run_generation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/LongMemEval/src/generation/run_generation.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/LongMemEval/src/retrieval/eval_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/personabench_data/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/personabench_data/main_batch.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/personabench_data/personabench/utils/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/personabench_data/personabench/utils/run_test.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/RF_mem/personamem_data/main_batch.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
