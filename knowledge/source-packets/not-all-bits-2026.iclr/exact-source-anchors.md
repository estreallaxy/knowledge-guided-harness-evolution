# Exact source anchors

## Selected mechanism

Allocate inference memory between model weights and KV cache according to model scale, task, and measured accuracy-throughput trade-offs.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.17; `paper/paper-iclr2026.txt` marker `===== PDF p.17 =====` | Experimental setup |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/score_prm_bestof.py:15` | `read_results_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/score_prm_bestof.py:90` | `extract_reasoning_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/score_prm_bestof.py:107` | `build_input_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/calculate_memory.py:40` | `_get_model_weight_size_gb` | Pinned implementation entry for the selected mechanism. |
| `official-code/calculate_memory.py:90` | `_parse_eviction_label` | Pinned implementation entry for the selected mechanism. |
| `official-code/calculate_memory.py:114` | `_kv_bytes_per_token_from_row` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/util/metrics.py:9` | `_pass_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/util/metrics.py:20` | `pass_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/ifeval/ifeval_scorer.py:12` | `process_results` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/ifeval/ifeval_scorer.py:31` | `IfEvalScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/math/math_scorer.py:15` | `MathEqualScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/math/math_scorer.py:42` | `MathVerifyScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/gsm8k/gsm8k_scorer.py:9` | `GSM8KScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/taco/taco_scorer.py:13` | `TACOScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/taco/taco_scorer.py:50` | `_taco_run_tests_mp` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/taco/taco_scorer.py:79` | `_temp_run_ray` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/apps/apps_scorer.py:17` | `APPSScorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/skythought/evals/scoring/apps/apps_scorer.py:91` | `_temp_run_ray` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `1c01319ad4d4069c8c0704ad965f25e079c4926f`. Paper page numbers refer to the fixed local proceedings PDF.
