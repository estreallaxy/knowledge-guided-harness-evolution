# Exact source anchors

## Selected mechanism

Guided by this insight, we introduce CapKV, a capacity-aware eviction method that directly targets information preservation via a log-determinant approximation using statistical leverage scores.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | method |
| Experimental setup | PDF p.15; `paper/paper-icml2026.txt` marker `===== PDF p.15 =====` | Experimental setup |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/cap_press.py:16` | `CapPress` | Pinned implementation entry for the selected mechanism. |
| `official-code/base_press.py:38` | `BasePress` | Pinned implementation entry for the selected mechanism. |
| `official-code/record_mixin.py:12` | `CapacityLoggerMixin` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `cf9c89429a19cabb5ae44621c185ee74b1f7b89e`. Paper page numbers refer to the fixed local proceedings PDF.
