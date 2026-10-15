# Exact source anchors

## Selected mechanism

Store per-page key minima/maxima, estimate query-dependent page criticality, and load only top-k KV pages for attention.

## Paper anchors

- p. 4: algorithm that exploits query-aware context sparsity, which After deriving the upper bound attention weights, we choose
- p. 5: Algorithm 1 Token Criticality Estimation Method / Budget 32 64 128 256 512
- p. 8: framework into real-world single-batch scenarios. We mea- we compare the inference efficiency of different attention

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
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
- `scripts/example_demo.py`
- `scripts/example_textgen.py`
- `evaluation/LongBench/eval.py`
- `evaluation/LongBench/metrics.py`
- `evaluation/LongBench/pred.py`
- `evaluation/passkey/passkey.py`
- `evaluation/pg19/ppl_eval.py`
- `quest/models/QuestAttention.py`
- `quest/utils/kv_cache.py`
- `quest/__init__.py`
- `scripts/bench_efficiency_e2e.sh`
- `scripts/bench_kernels.sh`
- `scripts/bench_textgen.py`
- `scripts/longbench.sh`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Quest is an inference-time sparse-attention algorithm with no training. The paper reports latency/accuracy trade-offs; code includes kernels, page summaries, top-k selection, examples, and benchmarks.

## Symbol-level code anchors

- `evaluation/quest_attention.py:23` — `local_heavy_hitter_mask`
- `quest/tests/test_approx_attention.py:10` — `assert_close`
- `quest/tests/test_decode_attention.py:10` — `assert_close`
- `quest/tests/test_prefill_attention.py:10` — `assert_close`
- `evaluation/llama.py:38` — `old_flash_attention_2_forward`
- `evaluation/mistral.py:37` — `old_flash_attention_2_forward`
- `quest/tests/test_estimate.py:10` — `assert_close`
- `quest/tests/test_rope.py:9` — `assert_close`
- `quest/tests/test_topk.py:15` — `assert_close`
- `scripts/example_demo.py:25` — `GenCtx`
- `evaluation/LongBench/eval.py:42` — `parse_args`
- `evaluation/LongBench/metrics.py:12` — `normalize_answer`
