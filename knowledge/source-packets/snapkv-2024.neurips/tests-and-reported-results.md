# Tests and reported results

## Official verification entry points

- `experiments/LongBench/eval.py`

## Published result anchors

- p. 9: Table 1: Performance comparison of SnapKV and H2O across various LLMs on LongBench.
- p. 10: Table 2: The sensitivity analysis was conducted on Mistral-7B-Instruct-v0.2 with a prompt
- p. 15: Table 3: Sequence Length Statistics for LongBench Benchmark

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2024 |
| Official open-source implementation | https://github.com/FasterDecoding/SnapKV at `e216ddc84c5bd210378cbdbbba12ba02102aa640` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
