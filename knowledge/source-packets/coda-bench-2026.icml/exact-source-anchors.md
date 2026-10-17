# Exact source anchors

## Selected mechanism

Retain the data-intensive Linux sandbox, code-and-data task construction, filesystem exploration protocol, and executable success evaluation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | System |
| Results and ablations | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | analysis |
| Limitations or failure conditions | PDF p.37; `paper/paper-icml2026.txt` marker `===== PDF p.37 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/examples/evaluate_predictions.py:11` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_dataset_setup.py:18` | `make_archive` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_dataset_setup.py:36` | `test_extract_layout_and_stale_directory` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_dataset_setup.py:48` | `test_bad_checksum_keeps_existing_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/load_dataset.py:14` | `load_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/load_dataset.py:20` | `print_task_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/load_dataset.py:40` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/setup_dataset.py:27` | `verify_archive` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/setup_dataset.py:35` | `extract_archive` | Pinned implementation entry for the selected mechanism. |
| `official-code/docker/openhands/openhands-sdk.py:30` | `_patch_sanitized_env` | Pinned implementation entry for the selected mechanism. |
| `official-code/docker/openhands/openhands-sdk.py:64` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/coda_bench/evaluation.py:9` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/coda_bench/evaluation.py:15` | `numeric_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/coda_bench/evaluation.py:20` | `exact_match` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/run_evaluation.py:34` | `EvaluationRunner` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/run_evaluation.py:270` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/coda_bench/schema.py:8` | `Task` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `23208c599d298e8912bfde9c88d3e4f4a4fa771b`. Paper page numbers refer to the fixed local proceedings PDF.
