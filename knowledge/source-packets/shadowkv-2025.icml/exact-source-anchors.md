# Exact source anchors

## Selected mechanism

Keep low-rank key representations on GPU, offload full values/keys, and fetch only sparse selected chunks for each query/head.

## Paper anchors

- p. 5: Algorithm 1 S HADOW KV Pre-filling Algorithm 2 S HADOW KV Decoding
- p. 8: Results. As shown in Table 3, S HADOW KV demonstrates under 1M contexts in Appendix A.6, demonstrating that

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.py`
- `kernels/test_cached_gather_copy.cu`
- `test/eval_acc.py`
- `test/evaluator.py`
- `kernels/test_gather_copy.cu`
- `test/e2e.py`
- `kernels/main.cu`
- `models/kv_cache.py`
- `models/prompt_template.py`
- `kernels/array_math.h`
- `kernels/batch_gather_gemm.cu`
- `kernels/batch_gather_gemm_epilogue.h`
- `kernels/batch_gemm_linear_combination.h`
- `kernels/batch_gemm_softmax.cu`
- `kernels/batch_gemm_softmax.h`
- `kernels/batch_gemm_with_epilogue_visitor.h`
- `kernels/copy.cuh`
- `kernels/functions.h`
- `kernels/gather_copy.cu`
- `kernels/gemm_universal_batch_gather_indices.h`
- `kernels/map.cuh`
- `kernels/rope.cu`
- `kernels/rope_new.cu`
- `kernels/special_batch_gather_predicated_tile_iterator.h`
- `models/__init__.py`
- `models/base.py`
- `models/glm.py`
- `models/llama.py`
- `models/phi3.py`
- `models/qwen.py`
- `models/tensor_op.py`
- `scripts/build_datasets.sh`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The method is explicitly training-free. ICML experiments report throughput and accuracy; code contains kernels, offload/cache managers, MInference compatibility, and evaluation scripts.

## Symbol-level code anchors

- `test/eval_acc.py:36` — `DistConfig`
- `test/evaluator.py:31` — `Evaluator`
- `test/e2e.py:119` — `parse_args`
- `models/kv_cache.py:25` — `KV_Cache`
- `kernels/batch_gather_gemm_epilogue.h:125` — `GatherRopeEpilogue`
- `kernels/batch_gemm_linear_combination.h:68` — `BatchGEMMLinearCombination`
- `kernels/batch_gemm_softmax.h:66` — `ApplySoftmax`
- `kernels/gemm_universal_batch_gather_indices.h:85` — `GemmUniversalBatchGatherIndices`
- `kernels/special_batch_gather_predicated_tile_iterator.h:46` — `SpecialPredicatedTileAccessIterator`
- `models/__init__.py:23` — `choose_model_class`
- `models/base.py:31` — `LLM`
- `models/glm.py:35` — `GLMLayer`
