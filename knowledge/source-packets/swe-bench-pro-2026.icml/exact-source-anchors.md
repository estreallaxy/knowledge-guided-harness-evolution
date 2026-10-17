# Exact source anchors

## Selected mechanism

We present SWE-Bench Pro, a comprehensive benchmark designed to evaluate software engineering capabilities through complex, realistic programming challenges.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.14; `paper/paper-icml2026.txt` marker `===== PDF p.14 =====` | Method |
| Results and ablations | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | Results |
| Limitations or failure conditions | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 7. Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/swe_bench_pro_eval.py:57` | `load_base_docker` | Pinned implementation entry for the selected mechanism. |
| `official-code/swe_bench_pro_eval.py:61` | `instance_docker` | Pinned implementation entry for the selected mechanism. |
| `official-code/swe_bench_pro_eval.py:65` | `load_local_script` | Pinned implementation entry for the selected mechanism. |
| `official-code/helper_code/create_problem_statement.py:14` | `create_problem_statement` | Pinned implementation entry for the selected mechanism. |
| `official-code/helper_code/generate_sweagent_instances.py:25` | `generate_instances` | Pinned implementation entry for the selected mechanism. |
| `official-code/helper_code/generate_sweagent_instances.py:65` | `write_yaml` | Pinned implementation entry for the selected mechanism. |
| `official-code/helper_code/generate_sweagent_instances.py:83` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tooling/patch_replay.py:25` | `PatchReplayAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tooling/locked_claude_code.py:21` | `LockedClaudeCode` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tooling/locked_mini_swe.py:18` | `LockedMiniSwe` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tooling/locked_codex.py:25` | `LockedCodex` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tooling/host_mini_swe.py:36` | `HarborSandboxEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tooling/host_mini_swe.py:79` | `HostMiniSweAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tasks/instance_flipt-io__flipt-f808b4dd6e36b9dc8b011eb26b196f4e2cc64c41/tests/parser.py:32` | `TestStatus` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tasks/instance_flipt-io__flipt-f808b4dd6e36b9dc8b011eb26b196f4e2cc64c41/tests/parser.py:42` | `TestResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tasks/instance_flipt-io__flipt-f808b4dd6e36b9dc8b011eb26b196f4e2cc64c41/tests/parser.py:52` | `parse_test_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tasks/instance_flipt-io__flipt-f743945d599b178293e89e784b3b2374b1026430/tests/parser.py:32` | `TestStatus` | Pinned implementation entry for the selected mechanism. |
| `official-code/v2/tasks/instance_flipt-io__flipt-f743945d599b178293e89e784b3b2374b1026430/tests/parser.py:42` | `TestResult` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `66f92766bba642462d4bbe5479e83f91f9211862`. Paper page numbers refer to the fixed local proceedings PDF.
