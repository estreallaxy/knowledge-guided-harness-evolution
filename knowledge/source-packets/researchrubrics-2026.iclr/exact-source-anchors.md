# Exact source anchors

## Selected mechanism

Represent deep-research quality as task-specific evidence-backed rubrics and apply them consistently to long-form outputs.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | framework |
| Results and ablations | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | results |
| Limitations or failure conditions | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/calculate_metrics/calculate_compliance_score.py:10` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate_rubrics/evaluate_reports_batch.py:25` | `evaluate_all_reports` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate_rubrics/evaluate_reports_batch.py:139` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate_rubrics/evaluate_single_report.py:51` | `EvaluationResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate_rubrics/evaluate_single_report.py:65` | `ImprovedPromptTemplates` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluate_rubrics/evaluate_single_report.py:75` | `RubricEvaluator` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2dc80e2d4c38ddd80439517c259d93c6954b193f`. Paper page numbers refer to the fixed local proceedings PDF.
