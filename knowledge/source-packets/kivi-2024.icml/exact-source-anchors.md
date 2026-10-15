# Exact source anchors

## Selected mechanism

Quantize key cache per channel and value cache per token while preserving a recent full-precision residual window.

## Paper anchors

- p. 3: method in Section 3.1. Our observations suggest that key dequantizing it in the attention layer. For per-channel quan-
- p. 5: Algorithm. As we previously analyzed, key cache should length R, the most outdated value cache is poped. Then the
- p. 6: Algorithm 1 for quantization is set as 32 across all experi- LM-Eval Results. We benchmark KIVI on CoQA, Truth-
- p. 6: evaluation, respectively1 . For LM-eval, we adopt CoQA
- p. 9: algorithm without the need for any tuning. In real LLM Alistarh. Gptq: Accurate post-training quantization
- p. 11: Algorithm 1: The KIVI Prefill & Decoding Algorithm

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `requirements.txt`
- `quant/setup.py`
- `config/dataset2prompt.json`
- `long_context_example.py`
- `mem_spd_test.py`
- `config/dataset2maxlen.json`
- `config/model2maxlen.json`
- `config/model2path.json`
- `quant/test.py`
- `scripts/long_test.sh`
- `eval_long_bench.py`
- `example.py`
- `metrics.py`
- `pred_long_bench.py`
- `models/llama_kivi.py`
- `models/mistral_kivi.py`
- `models/utils_quant.py`
- `quant/gemv.py`
- `quant/matmul.py`
- `quant/new_pack.py`
- `quant/qmodule.py`
- `quant/timeit_v2.py`
- `utils/data.py`
- `utils/metrics.py`
- `utils/process_args.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The method is explicitly tuning-free. ICML experiments report memory/throughput/quality, and the official repository implements quantizers, cache layout, model integration, and evaluation.

## Symbol-level code anchors

- `quant/test.py:15` — `set_seed`
- `eval_long_bench.py:42` — `parse_args`
- `metrics.py:12` — `normalize_answer`
- `pred_long_bench.py:16` — `build_chat`
- `models/llama_kivi.py:19` — `LlamaAttention_KIVI`
- `models/mistral_kivi.py:58` — `repeat_kv_quant`
- `models/utils_quant.py:33` — `SymQuantizer`
- `quant/gemv.py:17` — `gemv_kernel_g64`
- `quant/matmul.py:10` — `qbvm_kernel`
- `quant/new_pack.py:8` — `quant_and_pack_kcache`
- `quant/qmodule.py:6` — `make_divisible`
- `quant/timeit_v2.py:70` — `inner`
