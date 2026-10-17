# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/configs/build.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/docs/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/src/clonemem-eval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/clonemem/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/clonemem/common/config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/clonemem-eval/eval/run_eval.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/clonemem-eval/eval/run_generation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/clonemem-eval/eval_amem.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/clonemem-eval/eval_flat.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/clonemem-eval/eval_mem0.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/clonemem-eval/eval_oracle.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/clonemem/cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
