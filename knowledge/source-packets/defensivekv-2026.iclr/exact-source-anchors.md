# Exact source anchors

## Selected mechanism

Detect fragile KV-eviction decisions and preserve context tokens needed for robust long-context inference.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.13; `paper/paper-iclr2026.txt` marker `===== PDF p.13 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | method |
| Results and ablations | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluation/zero_scrolls/calculate_metrics.py:5` | `calculate_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/ruler/calculate_metrics.py:10` | `string_match_part` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/ruler/calculate_metrics.py:19` | `string_match_all` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/ruler/calculate_metrics.py:46` | `calculate_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/loogle/calculate_metrics.py:14` | `get_bleu_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/loogle/calculate_metrics.py:25` | `get_rouge_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/loogle/calculate_metrics.py:31` | `get_meteor_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/longbench/calculate_metrics.py:18` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/longbench/calculate_metrics.py:37` | `normalize_zh_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/longbench/calculate_metrics.py:53` | `count_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/infinite_bench/calculate_metrics.py:15` | `calculate_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/infinite_bench/calculate_metrics.py:23` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/infinite_bench/calculate_metrics.py:42` | `normalize_zh_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/efficiency_evaluate.py:80` | `efficiency_evaluate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/evaluate.py:99` | `evaluate` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/scorer_press.py:17` | `ScorerPress` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/efficient_ada_scorer_press.py:18` | `EfficientAdaScorerPress` | Pinned implementation entry for the selected mechanism. |
| `official-code/kvpress/presses/cake_scorer_press.py:16` | `CakeScorerPress` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9251b95e7e282a6c18dd98ef6318dd489e639a58`. Paper page numbers refer to the fixed local proceedings PDF.
