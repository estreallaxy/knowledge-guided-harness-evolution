# Tests and reported results

## Official verification entry points

- `kernels/test_cached_gather_copy.cu`
- `test/eval_acc.py`
- `test/evaluator.py`
- `kernels/test_gather_copy.cu`
- `test/e2e.py`

## Published result anchors

- p. 6: Table 1. Performance comparison of different models and methods on RULER (left side of the table) and LongBench (right side of the
- p. 8: Table 3. Generation throughput (tokens/s) on an A100. The gray Table 4. Generation throughput (tokens/s) under varying batch
- p. 9: Table 7. Performance across different number of outlier chunks on
- p. 9: Table 5. Latency breakdown (ms) of a Transformer block of Llama- 8 (0.049 %) 100.00 100.00
- p. 14: Table 8. Performance of S HADOW KV and S HADOW KV+ across different models on RULER (Hsieh et al., 2024) evaluated at length of
- p. 14: Table 9. Performance of S HADOW KV and S HADOW KV+ on different models with LongBench (Bai et al., 2023) samples exceeding 4K
- p. 15: Table 10. Performance of Yi-9B-200K with different methods on RULER (Hsieh et al., 2024) evaluated at length of 128K. S HADOW KV
- p. 15: Table 11. Performance of Yi-9B-200K with LongBench (Bai et al., 2023) samples exceeding 4K tokens. S HADOW KV outperforms other
- p. 16: Table 12. Performance comparison of S HADOW KV and baseline methods on the RULER (Hsieh et al., 2024) using FP8 precision,
- p. 16: Table 13. Evaluation of S HADOW KV and baseline methods on LongBench (Bai et al., 2023) with sequence lengths exceeding 4K tokens,

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICML 2025 (Spotlight) |
| Official open-source implementation | https://github.com/ByteDance-Seed/ShadowKV at `e51904cdeab7d4d34013370f09f2cf5fcd655e15` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
