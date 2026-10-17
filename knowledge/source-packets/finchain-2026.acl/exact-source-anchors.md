# Exact source anchors

## Selected mechanism

To address this gap, we introduce FinChain, the first benchmark specifically designed for verifiable Chain-of-Thought evaluation in finance.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | system |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 5 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 5.4 Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/chaineval/evaluate_predictions.py:46` | `read_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/chaineval/evaluate_predictions.py:54` | `bag_of_words_cosine` | Pinned implementation entry for the selected mechanism. |
| `official-code/chaineval/evaluate_predictions.py:70` | `parse_numeric_value` | Pinned implementation entry for the selected mechanism. |
| `official-code/website/static/js/index.js:7` | `preloadInterpolationImages` | Pinned implementation entry for the selected mechanism. |
| `official-code/website/static/js/index.js:14` | `setInterpolationImage` | Pinned implementation entry for the selected mechanism. |
| `official-code/website/static/js/bulma-slider.js:89` | `_classCallCheck` | Pinned implementation entry for the selected mechanism. |
| `official-code/website/static/js/bulma-slider.js:91` | `_possibleConstructorReturn` | Pinned implementation entry for the selected mechanism. |
| `official-code/website/static/js/bulma-slider.js:93` | `_inherits` | Pinned implementation entry for the selected mechanism. |
| `official-code/website/static/js/bulma-carousel.js:189` | `detectSupportsPassive` | Pinned implementation entry for the selected mechanism. |
| `official-code/website/static/js/bulma-carousel.js:274` | `_toConsumableArray` | Pinned implementation entry for the selected mechanism. |
| `official-code/website/static/js/bulma-carousel.js:276` | `_classCallCheck` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9bd2942b85d992844b77094a8b822aa16832703c`. Paper page numbers refer to the fixed local proceedings PDF.
