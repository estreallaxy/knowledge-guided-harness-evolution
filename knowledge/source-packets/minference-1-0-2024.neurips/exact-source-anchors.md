# Exact source anchors

## Selected mechanism

Profile attention patterns, choose sparse templates, and dynamically build sparse indices for each prompt during prefill.

## Paper anchors

- p. 4: results indicate that across layers and heads, the distances between nearest non-zero values are
- p. 5: Algorithm 1, we first create the search space based on ti ← FLOPs_in_kernel(σi )
- p. 5: approach leverages FlashAttention [Dao24] to reduce pbest ← argmin(yi − y, pbest )
- p. 5: Algorithm 2 Vertical-Slash Head Algorithm 3 Block-Sparse Head
- p. 6: method on three general long-context benchmarks: InfiniteBench [ZCH+ 24], RULER [HSK+ 24],
- p. 6: Implementation Details Our experiments use four state-of-the-art long-context LLMs: LLaMA-
- p. 6: results, we use greedy decoding in all experiments. We provide a simple custom implementation of
- p. 8: Ablation Study To evaluate the contributions
- p. 9: method is compatible with KV cache compression techniques. For most tasks, performance remains
- p. 22: results show that the 1M model also performs very well, with nearly perfect results in the Needle In
- p. 24: method offers a detailed and coherent narrative, comparable to the original, with a clear depiction of
- p. 24: method in generating high-quality, human-like summaries over the baseline methods.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `setup.cfg`
- `setup.py`
- `LeanK/README.md`
- `TriangleMix/README.md`
- `experiments/README.md`
- `mtraining/README.md`
- `mtraining/requirements.txt`
- `mtraining/setup.py`
- `scbench/readme.md`
- `scbench/requirements.txt`
- `TriangleMix/ruler/requirements.txt`
- `experiments/infinite_bench/requirements.txt`
- `experiments/ruler/requirements.txt`
- `LeanK/eval/test_memory.py`
- `examples/run_hf_streaming.py`
- `examples/run_hf_streaming.sh`
- `LeanK/eval/RULER/config_models.sh`
- `LeanK/eval/RULER/config_tasks.sh`
- `minference/dist_ops/test/run_ring_pytests.sh`
- `mtraining/model_configs/qwen2/modeling_qwen2.py`
- `.pre-commit-config.yaml`
- `LeanK/run_example.py`
- `TriangleMix/speed_test.py`
- `examples/run_hf.py`
- `examples/run_vllm.py`
- `minference/minference_configuration.py`
- `tests/test_e2e.py`
- `LeanK/eval/RULER/run.sh`
- `scbench/cache_blend.yaml`
- `scbench/compute_scores.py`
- `scbench/eval_utils.py`
- `scbench/run_scbench.py`
- `TriangleMix/ruler/config_models.sh`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The runtime patches pretrained models without training. The paper reports up-to-million-token accuracy/latency and code exposes HuggingFace/vLLM patches, sparse kernels, configs, and benchmarks.

## Symbol-level code anchors

- `setup.py:68` — `check_if_cuda_home_none`
- `LeanK/eval/test_memory.py:14` — `main`
- `examples/run_hf_streaming.py:18` — `greedy_generate`
- `mtraining/model_configs/qwen2/modeling_qwen2.py:54` — `Qwen2MLP`
- `TriangleMix/speed_test.py:87` — `get_kv_retrieval_prompt`
- `minference/minference_configuration.py:7` — `MInferenceConfig`
- `tests/test_e2e.py:23` — `MInferenceE2ETester`
- `scbench/compute_scores.py:21` — `normalize_answer`
- `scbench/eval_utils.py:143` — `check_benchmark_availability`
- `scbench/run_scbench.py:59` — `truncate_input`
- `experiments/needle_in_a_haystack/needle_test.py:16` — `Config`
- `minference/configs/model2path.py:75` — `get_support_models`
