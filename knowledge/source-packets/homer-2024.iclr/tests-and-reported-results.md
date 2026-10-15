# Tests and reported results

## Official verification entry points

- No standalone test filename was selected; evaluation logic remains identifiable through the retained runtime entry points.

## Published result anchors

- p. 7: Table 1: Retrieval accuracy on passkey retrieval. Average accuracy on 500 samples are reported.
- p. 8: Table 3: Perplexity of 25 long documents from PG-19 truncated to the evaluation length. The best
- p. 8: Table 4: Ablation on different components. We report the passkey retrieval accuracy for 500 sam-
- p. 9: Table 5: Peak memory usage for long inputs. All measurements are taken on a single A100 GPU,
- p. 16: Table 6: Prompt for passkey retrieval task. Slight modifications are made from the original prompt
- p. 16: Table 7: Prompt for question answering task. Basic prompt format follows Shaham et al. (2023).
- p. 17: Table 8: Inference time for long inputs. All measurements are taken on a single A100 GPU, with
- p. 19: Table 9.
- p. 19: Table 9: Perplexity values for passkey retrieval. Empty values indicate NaN.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/alinlab/HOMER at `822ef84ad77999657ee14ba4aa03c5c9fcc6988d` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
