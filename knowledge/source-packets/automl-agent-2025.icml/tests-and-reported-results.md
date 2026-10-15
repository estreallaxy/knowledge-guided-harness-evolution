# Tests and reported results

## Official verification entry points

- `experiments/evaluation.py`

## Published result anchors

- p. 3: Table 1. Comparison between AutoML-Agent and existing LLM-based frameworks.
- p. 7: Table 2. Summary of downstream tasks and datasets. erate about 2.3K instruction-response pairs using EvolIn-
- p. 15: Table 3. User instruction (i.e., task description) for experiments under the constraint-free setting.
- p. 16: Table 4. User instruction (i.e., task description) for experiments under the constraint-aware setting. Bold texts indicate constraints used
- p. 19: Table 5. Summary of downstream tasks and benchmark dataset statistics.
- p. 45: Table 6. Performance comparison with the SR metric. Best results are highlighted in bold.
- p. 46: Table 7. Performance comparison with the NPS metric. Best results are highlighted in bold.
- p. 46: Table 8. Performance comparison with the CS metric. Best results are highlighted in bold.
- p. 46: Table 9. Results of ablation study on different variations.
- p. 47: Table 10. Comparison between the different numbers of plans.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICML 2025 |
| Official open-source implementation | https://github.com/DeepAuto-AI/automl-agent at `9e0d842959a09d96c00768c14d73bd9df6d39023` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
