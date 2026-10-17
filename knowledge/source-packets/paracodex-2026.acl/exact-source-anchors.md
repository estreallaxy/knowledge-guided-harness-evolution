# Exact source anchors

## Selected mechanism

Autonomous coding agents can compile, test, and profile on target hardware, but outputs are brittle without domain scaffolding.We present ParaCodex, an HPC-engineer workflow that turns a Codex-based agent into an autonomous OpenMP GPU offload system using staged hotspot analysis, explicit data planning, correctness gating, and profiling-guided refinement.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4.1 Experimental Setup |
| Results and ablations | PDF p.4; `paper/paper-acl2026.txt` marker `===== PDF p.4 =====` | 1. Analysis |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 6 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/pipeline/agents/baseline_codex.py:51` | `_find_executable` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/baseline_codex.py:66` | `build_baseline_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/baseline_codex.py:111` | `run_baseline_for_kernel` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/common.py:38` | `parse_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/common.py:73` | `test_compilation` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/common.py:116` | `run_codex_command` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/supervisor_codex.py:62` | `run_make` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/supervisor_codex.py:97` | `infer_source_filename` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/supervisor_codex.py:160` | `build_supervise_session_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/initial_translation_codex.py:55` | `_build_serial_translation_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/initial_translation_codex.py:106` | `_build_cuda_translation_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/initial_translation_codex.py:156` | `_build_translation_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/optimize_codex.py:61` | `_build_nsys_profile_cmd` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/optimize_codex.py:74` | `_nsys_profile_cmd_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/pipeline/agents/optimize_codex.py:86` | `_cleanup_nsys_artifacts` | Pinned implementation entry for the selected mechanism. |
| `official-code/workdirs/serial_omp_hecbench_workdir/golden_labels/src/cmp-cuda/su_trace.hpp:33` | `su_trace` | Pinned implementation entry for the selected mechanism. |
| `official-code/workdirs/serial_omp_hecbench_workdir/golden_labels/src/cmp-cuda/su_trace.hpp:41` | `su_trace` | Pinned implementation entry for the selected mechanism. |
| `official-code/performance_testers/reprofile_fixed_benchmarks.py:18` | `clean_nsys_artifacts` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `5b4af3fdaffd3f63f4d66add52208d220a1914d3`. Paper page numbers refer to the fixed local proceedings PDF.
