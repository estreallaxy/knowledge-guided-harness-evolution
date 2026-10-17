# Exact source anchors

## Selected mechanism

Retain the training-free Delta Attention Selective Halting policy that monitors layer-wise update stability and stops redundant token computation at inference time.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | Method |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4 Experiments |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | Results |
| Limitations or failure conditions | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | 5 Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/presses/base_press.py:36` | `BasePress` | Pinned implementation entry for the selected mechanism. |
| `official-code/presses/delta_press.py:21` | `DeltaPress` | Pinned implementation entry for the selected mechanism. |
| `official-code/presses/delta_press_l_nr.py:20` | `DeltaPressLNR` | Pinned implementation entry for the selected mechanism. |
| `official-code/presses/mllm.py:18` | `DeltaPress` | Pinned implementation entry for the selected mechanism. |
| `official-code/presses/mllm.py:458` | `DeltaPressLNR` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `831cb45f2b41714aad719af1d7092604be94bc93`. Paper page numbers refer to the fixed local proceedings PDF.
