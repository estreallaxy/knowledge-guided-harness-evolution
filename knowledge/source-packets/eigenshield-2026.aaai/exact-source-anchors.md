# Exact source anchors

## Selected mechanism

We introduce EigenShield, a principled, inference-time, architecture-agnostic defense that leverages Random Matrix Theory (RMT) to suppress adversarial noise in high-dimensional embeddings.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-aaai2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-aaai2026.txt` marker `===== PDF p.5 =====` | method |
| Results and ablations | PDF p.2; `paper/paper-aaai2026.txt` marker `===== PDF p.2 =====` | results |
| Limitations or failure conditions | PDF p.4; `paper/paper-aaai2026.txt` marker `===== PDF p.4 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/eigenshield/evaluation/metrics.py:28` | `ToxicityScores` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/evaluation/metrics.py:54` | `PerspectiveAPIScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/evaluation/metrics.py:211` | `HarmClassifier` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/core/defense.py:21` | `EigenShieldConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/core/defense.py:51` | `EigenShield` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/core/defense.py:355` | `EigenShieldModule` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/attacks/jailbreak_prompts.py:12` | `JailbreakPromptGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/attacks/jailbreak_prompts.py:312` | `VLMJailbreakGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/attacks/jailbreak_prompts.py:361` | `load_harmbench_prompts` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/evaluate_llm.py:45` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/evaluate_llm.py:149` | `load_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/evaluate_llm.py:167` | `generate_calibration_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/evaluate_vlm.py:47` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/evaluate_vlm.py:174` | `load_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/evaluate_vlm.py:219` | `run_image_attack` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/evaluation/evaluator.py:35` | `EvaluationConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/evaluation/evaluator.py:63` | `EvaluationResults` | Pinned implementation entry for the selected mechanism. |
| `official-code/eigenshield/evaluation/evaluator.py:122` | `EigenShieldEvaluator` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `189ffef0cd5a04f5cd3f13e3c191f5ee1e3f9d3e`. Paper page numbers refer to the fixed local proceedings PDF.
