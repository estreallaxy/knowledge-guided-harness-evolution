# Exact source anchors

## Selected mechanism

To address these issues, we propose DEER, a benchmark for evaluating expert-level deep research reports.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | system |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 6. Experiments |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | ablation |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run_score_integration.py:31` | `_read` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_score_integration.py:34` | `_is_num` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_score_integration.py:37` | `_mean` | Pinned implementation entry for the selected mechanism. |
| `official-code/info_verification/eval_metrics.py:7` | `compute_claim_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/info_verification/eval_metrics.py:54` | `compute_citation_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/info_verification/eval_metrics.py:83` | `_hhi_from_counts` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_report_evaluation.py:102` | `_parse_samples` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_report_evaluation.py:125` | `_element_block_is_valid` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_report_evaluation.py:134` | `_validate_full` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_information_verification.py:14` | `_parse_samples` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_information_verification.py:67` | `_clip` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_information_verification.py:70` | `amount_to_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts/schemas.py:11` | `ScoreFactor` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts/schemas.py:22` | `CompletenessCriterion1` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts/schemas.py:28` | `CompletenessCriterion2` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts/prompt_report.py:1` | `get_prompt_request_fulfillment` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts/prompt_report.py:208` | `get_prompt_analytical_soundness` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts/prompt_report.py:445` | `get_prompt_structural_coherence` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `88580fc4dc502974a6748ca58edddf129b8a2044`. Paper page numbers refer to the fixed local proceedings PDF.
