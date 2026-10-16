# Exact source anchors

## Selected mechanism

Combine layer-wise reconstruction evidence with spatial-temporal smoothing for robust KV-cache eviction.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | framework |
| Experimental setup | PDF p.25; `paper/paper-iclr2026.txt` marker `===== PDF p.25 =====` | Experiments |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/metrics.py:12` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:31` | `normalize_zh_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:47` | `count_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_ema.py:3` | `ema` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_ema.py:15` | `test_ema` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_avgpool_shift.py:14` | `get_top_two_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_ruler.py:10` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:44` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:50` | `scorer_e` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:68` | `scorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_infinite.py:15` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_infinite.py:86` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_infinite.py:105` | `normalize_zh_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_ruler.py:47` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_ruler.py:56` | `build_chat` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_ruler.py:67` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_longbench.py:90` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_longbench.py:99` | `build_chat` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a8bb112312d2b2ec7b73d12eb66f865b62d1e754`. Paper page numbers refer to the fixed local proceedings PDF.
