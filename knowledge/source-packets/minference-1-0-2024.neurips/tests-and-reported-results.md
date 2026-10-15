# Tests and reported results

## Official verification entry points

- `LeanK/eval/test_memory.py`
- `LeanK/eval/RULER/config_models.sh`
- `LeanK/eval/RULER/config_tasks.sh`
- `minference/dist_ops/test/run_ring_pytests.sh`
- `TriangleMix/speed_test.py`
- `tests/test_e2e.py`
- `LeanK/eval/RULER/run.sh`
- `scbench/compute_scores.py`
- `scbench/eval_utils.py`
- `experiments/needle_in_a_haystack/needle_test.py`
- `scbench/scripts/test_llama.sh`
- `scbench/scripts/test_minference_with_snapkv.sh`
- `minference/dist_ops/test/minfer_ring_test.py`
- `minference/dist_ops/test/minfer_ring_test_raw.py`
- `minference/dist_ops/test/moba_ring_test.py`
- `minference/dist_ops/test/moba_ring_test_raw.py`
- `minference/dist_ops/test/raw_test_utils.py`
- `minference/dist_ops/test/xattn_ring_test.py`
- `minference/dist_ops/test/xattn_ring_test_raw.py`

## Published result anchors

- p. 3: Table 1: Comparison of different sparse patterns.
- p. 7: Table 2: Performance of different methods with different base models on InfiniteBench [ZCH+ 24].
- p. 7: Table 3: Performance (%) of different models and different methods on RULER [HSK+ 24] evaluated at lengths
- p. 9: Table 4: Performance of different ablation methods using LLaMA-3-8B-Instruct-262K on In-
- p. 9: Table 5: Performance of different methods on InfiniteBench [ZCH+ 24] using SnapKV [LHY+ 24] in the
- p. 9: Table 6: Performance of different methods using LLaMA-3-70B-Instruct-262K on InfiniteBench [ZCH+ 24].
- p. 19: Table 7: Kernal-aware optimal head pattern search space. In this context, A-shape represents the global tokens
- p. 22: Table 8: Performance of different ablation methods using LLaMA-3-8B-Instruct-262K on In-
- p. 25: Table 9: Comparison of generated results by different methods using LLaMA-3-8B-Instruct-262K in summariza-
- p. 27: Table 10: Comparison of generated results by different methods using LLaMA-3-8B-Instruct-262K in KV

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2024 |
| Official open-source implementation | https://github.com/microsoft/MInference at `29ef1974fcb5a1440ccf92d7d7996900230fddcf` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
