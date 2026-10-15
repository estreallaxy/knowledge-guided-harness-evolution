# Tests and reported results

## Official verification entry points

- `examples/eval_long_ppl.py`

## Published result anchors

- p. 5: Table 1: Window attention has poor per- Table 2: Effects of reintroduced initial token numbers on
- p. 7: Table 4: Zero-shot accuracy (in %) across 7 NLP benchmarks, including
- p. 8: Table 5: Accuracy (in %) on the ARC-[Easy, Challenge] datasets. Questions were concatenated and answered
- p. 9: Table 6: Effects of cache size on StreamingLLM’s
- p. 16: Table 7: Accuracy (in %) on StreamEval with increasing query-answer distance. Each line in StreamEval
- p. 17: Table 8: Performance comparison of StreamingLLM against the default truncation baseline in LongBench (Bai
- p. 21: Table 10: Comparison of vanilla attention with prepending a zero token and a learnable sink token
- p. 21: Table 9: Zero-shot accuracy (in %) across 7 NLP benchmarks,

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/mit-han-lab/streaming-llm at `2e5042606d69933d88fbf909bd77907456b9b4dd` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
