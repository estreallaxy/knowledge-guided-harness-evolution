# Exact source anchors

## Selected mechanism

Audit and mitigate contamination between generated data and LLM judges through controlled evaluator comparisons.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | experiments |
| Results and ablations | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | analysis |
| Limitations or failure conditions | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | limitation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/winrate.py:12` | `get_winrate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/winrate.py:24` | `pairwise_to_winrate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/helpers.py:14` | `BaseScoringRule` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/helpers.py:103` | `ZeroOneScoringRule` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/helpers.py:129` | `AbsoluteScoringRule` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/glm_winrate.py:44` | `get_length_controlled_winrate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/glm_winrate.py:152` | `predict_winrate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/metrics/glm_winrate.py:186` | `get_is_extreme_changes` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/decoders/cache.py:11` | `cache_completions` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/annotators/pairwise_evaluator.py:38` | `PairwiseAnnotatorLocal` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/annotators/pairwise_evaluator.py:323` | `PairwiseAnnotator` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/annotators/pairwise_evaluator.py:327` | `SinglePairwiseAnnotator` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/decoders/test.py:9` | `test_completions` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/tests/test_pairwise_evaluator.py:10` | `df_to_annotate` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/tests/test_pairwise_evaluator.py:21` | `expected_annotations` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/tests/test_pairwise_evaluator.py:48` | `single_annotator` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/constants.py:80` | `get_alpaca_eval_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/Alpaca_Eval2/src/alpaca_eval/constants.py:98` | `ALPACAEVAL_INSTRUCTION_PARAMETERS` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d6f7fcec4b8719c4b0a87c9b72548b2edb22a8c9`. Paper page numbers refer to the fixed local proceedings PDF.
