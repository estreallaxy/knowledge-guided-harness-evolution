# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/ENVIRONMENT.md` | Dependency, configuration, or usage evidence. |
| `official-code/setup_environment.sh` | Dependency, configuration, or usage evidence. |
| `official-code/verify_environment.sh` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/cuda_omp_pareval_workdir/golden_labels/src/microXOR-cuda/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/cuda_omp_pareval_workdir/golden_labels/src/microXORh-cuda/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/cuda_omp_pareval_workdir/golden_labels/src/nano-XOR-cuda/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_hecbench_workdir/golden_labels/src/bsearch-cuda/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_hecbench_workdir/golden_labels/src/interval-cuda/boost/config/no_tr1/memory.hpp` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_hecbench_workdir/golden_labels/src/testSNAP-cuda/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_anonymized_workdir/golden_labels/src/cg-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_anonymized_workdir/golden_labels/src/ep-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_anonymized_workdir/golden_labels/src/ft-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_workdir/golden_labels/src/bt-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_workdir/golden_labels/src/cg-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_workdir/golden_labels/src/ep-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_workdir/golden_labels/src/ft-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_workdir/golden_labels/src/lu-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |
| `official-code/workdirs/serial_omp_nas_workdir/golden_labels/src/mg-serial/config/NAS.samples/README` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/pipeline/agents/baseline_codex.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/pipeline/agents/common.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/pipeline/agents/supervisor_codex.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/pipeline/agents/initial_translation_codex.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/pipeline/agents/optimize_codex.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/workdirs/serial_omp_hecbench_workdir/golden_labels/src/cmp-cuda/su_trace.hpp` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/performance_testers/reprofile_fixed_benchmarks.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
