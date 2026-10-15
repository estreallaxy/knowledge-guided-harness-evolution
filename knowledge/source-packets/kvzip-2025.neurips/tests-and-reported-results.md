# Tests and reported results

## Official verification entry points

- `attention/score.py`
- `test.py`
- `utils/tester.py`
- `eval.py`

## Published result anchors

- p. 9: Table 1: Behavior analysis. Generation results on a privacy-related example from DecodingTrust
- p. 23: Table 2: Test performance of Qwen2.5-7B on SQuAD at a 30% KV cache ratio. Note, SnapKV
- p. 28: Table 3: Inputs for KV cache importance scoring from a SQuAD example (used in the visualizations
- p. 28: Table 4: Inputs for importance scoring from a GSM8K example used in the visualization in Figure 6,

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2025 (Oral) |
| Official open-source implementation | https://github.com/snu-mllab/KVzip at `5d8472975d286e3da6b52178af39d18904330c0d` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
