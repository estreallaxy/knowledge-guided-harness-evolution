# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/app/xsbench/src/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/2DCONV/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/2MM/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/3DCONV/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/3MM/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/ADI/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/ATAX/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/BICG/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/CORR/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/COVAR/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/DOITGEN/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/FDTD-2D/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/GEMM/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/GEMVER/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/GESUMMV/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/GRAMSCHM/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/JACOBI1D/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/cgo/poly/src/JACOBI2D/Makefile` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/benchmark/app/xsbench/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/llm/kbench/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/misc/nbody/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmark/misc/nbody/src/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
