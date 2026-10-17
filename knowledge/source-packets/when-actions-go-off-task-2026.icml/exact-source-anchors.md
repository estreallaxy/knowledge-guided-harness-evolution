# Exact source anchors

## Selected mechanism

Moreover, we propose DeAction, a practical and universal guardrail that detects misaligned actions before execution and iteratively corrects them through structured feedback.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Method |
| Experimental setup | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/DeAction/base_guardrail.py:9` | `BaseGuardrail` | Pinned implementation entry for the selected mechanism. |
| `official-code/DeAction/utils.py:10` | `parse_model_spec` | Pinned implementation entry for the selected mechanism. |
| `official-code/DeAction/utils.py:23` | `create_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/DeAction/utils.py:72` | `encode_image` | Pinned implementation entry for the selected mechanism. |
| `official-code/DeAction/narrative_summary.py:12` | `NarrativeSummaryGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/DeAction/run.py:29` | `_normalize_bool` | Pinned implementation entry for the selected mechanism. |
| `official-code/DeAction/run.py:43` | `_ensure_directory` | Pinned implementation entry for the selected mechanism. |
| `official-code/DeAction/run.py:49` | `BenchmarkEntry` | Pinned implementation entry for the selected mechanism. |
| `official-code/DeAction/deaction.py:42` | `DeAction` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9ce1fee5dfe7525ef341fdb76180fc8fba5cc099`. Paper page numbers refer to the fixed local proceedings PDF.
