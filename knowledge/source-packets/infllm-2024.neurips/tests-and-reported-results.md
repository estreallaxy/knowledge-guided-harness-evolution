# Tests and reported results

## Official verification entry points

- `benchmark/config/dataset2prompt.json`
- `benchmark/eval.py`
- `benchmark/infinitebench_eval.py`
- `benchmark/config/dataset2maxlen.json`
- `benchmark/download.py`
- `benchmark/merge.py`
- `benchmark/metrics.py`
- `benchmark/pred.py`
- `scripts/multiprocessing-benchmark.sh`

## Published result anchors

- p. 6: Table 1: The results of InfLLM and baseline models on ∞-Bench. The 95% quantile for text lengths
- p. 7: Table 2: The comparison between InfLLM and models with continual pre-training, Llama-3-8B-
- p. 16: Table 5: The results of InfLLM and baseline models on LongBench. The 95% quantile for text
- p. 18: Table 7: The combination of InfLLM and models with continual pre-training, Yi-9B-200K (Yi-
- p. 18: Table 7. From the results, we can observe that InfLLM can also achieve comparable results with

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2024 |
| Official open-source implementation | https://github.com/thunlp/InfLLM at `12b70798f56e56ebb23c53c7018091a3f540a028` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
