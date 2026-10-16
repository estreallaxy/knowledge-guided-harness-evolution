# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README_zh.md` | Dependency, configuration, or usage evidence. |
| `official-code/csrc/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/csrc/makefile` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/eval_infinite.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/eval_ruler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_infinite_bench.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_longbench.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_needle_in_haystack.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_ruler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/infinite_bench/eval.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/infinite_bench/run_llama3.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/longbench/eval.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/longbench/run.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/longbench/run_gemma.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/longbench/run_llama2.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/longbench/run_llama3.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/longbench/run_llama3_70b.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/longbench/run_mistral.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
