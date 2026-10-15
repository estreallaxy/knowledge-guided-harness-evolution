# Tests and reported results

## Official verification entry points

- `evaluation/LongBench/config/dataset2prompt.json`
- `evaluation/quest_attention.py`
- `quest/tests/test_approx_attention.py`
- `quest/tests/test_decode_attention.py`
- `quest/tests/test_prefill_attention.py`
- `evaluation/LongBench/config/dataset2maxlen.json`
- `evaluation/LongBench/config/model2maxlen.json`
- `evaluation/LongBench/config/model2path.json`
- `evaluation/llama.py`
- `evaluation/mistral.py`
- `scripts/ppl_eval.sh`
- `quest/tests/test_estimate.py`
- `quest/tests/test_rope.py`
- `quest/tests/test_topk.py`
- `kernels/src/test/test_batch_decode.cu`
- `kernels/src/test/test_max_possible.cu`
- `kernels/src/test/test_page.cu`
- `kernels/src/test/test_prefill.cu`
- `evaluation/LongBench/eval.py`
- `evaluation/LongBench/metrics.py`
- `evaluation/LongBench/pred.py`
- `evaluation/passkey/passkey.py`
- `evaluation/pg19/ppl_eval.py`

## Published result anchors

- p. 5: Table 1. (i) Results of 10k length passkey retrieval test on

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICML 2024 |
| Official open-source implementation | https://github.com/mit-han-lab/Quest at `01c1623bf9395009520874e989e29f683203b357` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
