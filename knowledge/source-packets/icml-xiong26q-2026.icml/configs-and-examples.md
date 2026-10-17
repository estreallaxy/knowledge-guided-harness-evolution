# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Block-Sparse-Attention/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/Block-Sparse-Attention/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/Block-Sparse-Attention/block_sparse_attn/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/Block-Sparse-Attention/csrc/block_sparse_attn/src/namespace_config.h` | Dependency, configuration, or usage evidence. |
| `official-code/Block-Sparse-Attention/csrc/cutlass/LICENSE.txt` | Dependency, configuration, or usage evidence. |
| `official-code/Block-Sparse-Attention/csrc/cutlass/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/Block-Sparse-Attention/csrc/cutlass/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/Block-Sparse-Attention/csrc/cutlass/setup.cfg` | Dependency, configuration, or usage evidence. |
| `official-code/Block-Sparse-Attention/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/legacy/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/legacy/boundary_predictor/flags_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/legacy/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/legacy/utils/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/legacy/utils/flags_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_configuration.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/test_density_config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/eval_longbench.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/eval_ruler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/legacy/eval_longbench.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/legacy/run_latency_test.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/legacy/scripts/run_eval_longbench_res.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/legacy/scripts/run_latency_test.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_longbench.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_needle_in_haystack.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_ruler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/eval_longbench.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/eval_ruler.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
