# Exact source anchors

## Selected mechanism

Score cached KV pairs by how well they reconstruct the original context, then evict low-importance pairs once for reuse across future queries.

## Paper anchors

- p. 2: results in suboptimal performance due to a mismatch with their original designs (Section 4).
- p. 3: 3 Method
- p. 3: method supports both non-uniform and uniform head budget allocations [17, 33]. KVzip further
- p. 6: 4 Experiment
- p. 6: Evaluation. Our evaluation focuses on the capability of a KV cache to effectively handle diverse
- p. 7: method significantly outperforms baselines, preserving performance at a 30% cache ratio except
- p. 7: method robustly generalizes across diverse tasks in query-agnostic settings, outperforming baseline
- p. 12: algorithm for training recurrent networks. Advances in neural information processing systems,
- p. 14: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 15: implementation details in Section 4.1 and Appendix A.
- p. 16: results?
- p. 19: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `requirements.txt`
- `csrc/LICENSE`
- `model/quant_model/README.md`
- `model/quant_model/setup.py`
- `attention/kvcache.py`
- `attention/score.py`
- `test.py`
- `utils/tester.py`
- `eval.py`
- `attention/attn.py`
- `args.py`
- `demo.py`
- `csrc/build.py`
- `model/__init__.py`
- `model/load.py`
- `model/monkeypatch.py`
- `model/template.py`
- `model/wrapper.py`
- `utils/__init__.py`
- `utils/func.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. KVzip is a query-agnostic inference-time compressor and does not update weights. Main-track experiments report reuse, quality, memory, and latency; official code implements scoring, eviction, and demos.

## Symbol-level code anchors

- `attention/kvcache.py:14` — `EvictCache`
- `attention/score.py:12` — `KVScore`
- `utils/tester.py:4` — `Evaluator`
- `eval.py:4` — `set_ratios`
- `attention/attn.py:19` — `llama_qwen_attn_forward`
- `csrc/build.py:35` — `get_cuda_bare_metal_version`
- `model/load.py:5` — `get_model_id`
- `model/monkeypatch.py:5` — `replace_attn`
- `model/template.py:1` — `template`
- `model/wrapper.py:18` — `chunk_fn`
- `utils/func.py:7` — `set_gen_length`
