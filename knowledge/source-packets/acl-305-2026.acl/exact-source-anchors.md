# Exact source anchors

## Selected mechanism

Towards this end, we propose an innovative framework named Sequence-level risk Accumulation for calibrating test-time alignment (SEAT).

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | framework |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4.3 Ablation |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 6 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/safety_risk_utils.py:6` | `squash_safety_logits` | Pinned implementation entry for the selected mechanism. |
| `official-code/safety_risk_utils.py:16` | `compute_step_risk` | Pinned implementation entry for the selected mechanism. |
| `official-code/safety_risk_utils.py:71` | `update_sequence_risk` | Pinned implementation entry for the selected mechanism. |
| `official-code/baseline/smooth-llm/lib/defenses.py:9` | `Defense` | Pinned implementation entry for the selected mechanism. |
| `official-code/baseline/smooth-llm/lib/defenses.py:37` | `SmoothLLM` | Pinned implementation entry for the selected mechanism. |
| `official-code/baseline/smooth-llm/lib/attacks.py:4` | `Prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/baseline/smooth-llm/lib/attacks.py:18` | `Attack` | Pinned implementation entry for the selected mechanism. |
| `official-code/baseline/smooth-llm/lib/attacks.py:24` | `GCG` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_eval.py:43` | `call_safety_api` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_eval.py:61` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/toxicity.py:14` | `Sess` | Pinned implementation entry for the selected mechanism. |
| `official-code/toxicity.py:61` | `SearchNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/toxicity.py:70` | `MCTSNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/seat.py:15` | `SearchNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/seat.py:27` | `Gen` | Pinned implementation entry for the selected mechanism. |
| `official-code/baseline/smooth-llm/lib/perturbations.py:4` | `Perturbation` | Pinned implementation entry for the selected mechanism. |
| `official-code/baseline/smooth-llm/lib/perturbations.py:12` | `RandomSwapPerturbation` | Pinned implementation entry for the selected mechanism. |
| `official-code/baseline/smooth-llm/lib/perturbations.py:27` | `RandomPatchPerturbation` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `85d955d097eb65300a396f4bb190296484e4c649`. Paper page numbers refer to the fixed local proceedings PDF.
