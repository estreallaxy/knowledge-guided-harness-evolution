# Tests and reported results

## Official verification entry points

- `mem_spd_test.py`
- `quant/test.py`
- `scripts/long_test.sh`
- `eval_long_bench.py`

## Published result anchors

- p. 7: Table 3: Performance comparison between 16bit, 4-bit per-
- p. 8: Table 4: Performance evaluation of KIVI on various models across a range of benchmarks in LongBench. We highlight the
- p. 8: Table 5: Ablation study of KIVI by changing group size G et al., 2023; Wang et al., 2023; 2022). Among them,
- p. 12: Table 6: Performance comparison between 16bit, KIVI-2 (2bit) / KIVI-4 (4bit) with residual length 128 and 32 across
- p. 12: Table 7: Performance evaluation of KIVI with residual length 128 and 32 on various models across a range of benchmarks
- p. 13: Table 8: The results of LongChat-7B-v1.5-32K with KIVI on LongBench. The model has 32K context length. We use a 32
- p. 13: Table 9: The results of Mistral-7B-Instruct-v0.2 with KIVI on LongBench. The model has 32K context length and applies

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICML 2024 |
| Official open-source implementation | https://github.com/jy-yuan/KIVI at `876b4d2d08e3b1d5f70d0969c299d8c7c42ddfb6` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
