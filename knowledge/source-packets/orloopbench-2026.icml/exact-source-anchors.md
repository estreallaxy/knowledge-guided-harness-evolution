# Exact source anchors

## Selected mechanism

We introduce ORLoopBench , a benchmark suite with two components: ORDebug releases 5,362 LP/MILP repair instances, while ORBias evaluates closed-form operational decision rationality across inventory settings.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.11; `paper/paper-icml2026.txt` marker `===== PDF p.11 =====` | framework |
| Experimental setup | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | 2. Benchmark Setup |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 5.6. Ablation |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 2024. Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/scripts/validate_benchmarks.py:15` | `load_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/validate_benchmarks.py:20` | `validate_ordebug` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/validate_benchmarks.py:55` | `validate_orbias` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `4739df0e8dbb3d38a9ff93d96c222acc71a4f6ef`. Paper page numbers refer to the fixed local proceedings PDF.
