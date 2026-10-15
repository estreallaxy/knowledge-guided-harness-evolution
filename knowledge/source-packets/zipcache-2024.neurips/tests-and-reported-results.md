# Tests and reported results

## Official verification entry points

- No standalone test filename was selected; evaluation logic remains identifiable through the retained runtime entry points.

## Published result anchors

- p. 5: Table 1: Performance comparisons of different quantization granularities for KV cache. The KV
- p. 7: Table 2: Performance comparisons of
- p. 8: Table 3: Performance comparisons on GSM8k with CoT prompts. Here, "H/L" denotes the bit-width
- p. 9: Table 4: Performance comparisons on HumanEval for code generation. Here, "H/L" denotes the

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2024 |
| Official open-source implementation | https://github.com/ThisisBillhe/ZipCache at `8833f675a938b019fccc531bfdf932abe6e622ad` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
