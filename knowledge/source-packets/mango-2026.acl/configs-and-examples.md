# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/evaluation/baselines/webwalker/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/preprocess/run_preprocessing.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webvoyager/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webvoyager/evaluate.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webvoyager/rebuttal/run_embedding_scoring.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webvoyager/rebuttal/run_greedy_baseline.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webvoyager/rebuttal/run_no_memory_ablation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webvoyager/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webvoyager/run.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webwalker/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webwalker/evaluate.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webwalker/rebuttal/run_embedding_scoring.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webwalker/rebuttal/run_greedy_baseline.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webwalker/rebuttal/run_kappa_sweep.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webwalker/rebuttal/run_no_memory_ablation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/evaluation/scripts/webwalker/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
