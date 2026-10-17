# Exact source anchors

## Selected mechanism

We propose a simple plug-in framework that corrects this bias and enables statistically principled uncertainty quantification.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | 4. Method |
| Results and ablations | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | analysis |
| Limitations or failure conditions | PDF p.12; `paper/paper-icml2026.txt` marker `===== PDF p.12 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/llm_judge_reporting/allocation.py:7` | `allocate_calibration_sample` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_judge_reporting/calibration.py:7` | `clip` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_judge_reporting/calibration.py:11` | `point_estimator` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_judge_reporting/calibration.py:29` | `confidence_interval` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `082884d075188bed2f2645234fa2cc3050a517c5`. Paper page numbers refer to the fixed local proceedings PDF.
