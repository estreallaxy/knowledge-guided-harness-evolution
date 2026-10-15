# Exact source anchors

## Selected mechanism

Move distant tokens into memory units and retrieve query-relevant units into a bounded active attention window.

## Paper anchors

- p. 3: 3 Methodology
- p. 4: method to assign positional embeddings for selected relevant memory units and cache management
- p. 5: approach allows for efficient encoding of extremely long sequences using limited GPU memory.
- p. 6: 4.2 Implementation Details
- p. 7: results with only 8K context window. It indicates that InfLLM can also serve as an efficient way to
- p. 9: 4.7 Ablation Study
- p. 9: ablation studies in this section. The results are shown in Table 4.
- p. 9: evaluation. We adopt Mistral as the base model.
- p. 15: Limitations
- p. 16: results are illustrated in Figure 4. It is observable that the LRU strategy we employed exhibits a
- p. 19: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 21: results?

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.py`
- `config/mistral-stream-llm.yaml`
- `config/vicuna-stream-llm.yaml`
- `benchmark/config/dataset2prompt.json`
- `config/llama-3-inf-llm.yaml`
- `config/minicpm-inf-llm.yaml`
- `config/mistral-inf-llm-12k.yaml`
- `config/mistral-inf-llm-fattn.yaml`
- `config/mistral-inf-llm.yaml`
- `config/mistral-infinite-lm.yaml`
- `config/mistral-ntk.yaml`
- `config/mistral-origin.yaml`
- `config/mistral-pi.yaml`
- `config/qwen-inf-llm.yaml`
- `config/vicuna-inf-llm.yaml`
- `config/vicuna-infinite-lm.yaml`
- `config/vicuna-origin.yaml`
- `inf_llm/attention/context_manager.py`
- `inf_llm/attention/stream_llm.py`
- `benchmark/eval.py`
- `benchmark/infinitebench_eval.py`
- `benchmark/config/dataset2maxlen.json`
- `inf_llm/attention/__init__.py`
- `inf_llm/attention/inf_llm.py`
- `inf_llm/attention/infinite_lm.py`
- `inf_llm/attention/origin.py`
- `inf_llm/attention/rope.py`
- `inf_llm/attention/utils.py`
- `inf_llm/utils/greedy_search.py`
- `inf_llm/attention/dot_production_attention/__init__.py`
- `inf_llm/attention/dot_production_attention/base.py`
- `inf_llm/attention/dot_production_attention/torch_impl.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The method is explicitly training-free and evaluated up to very long contexts. The repository includes memory lookup, multi-stage attention, configs, chat integration, and LongBench/InfiniteBench scripts.

## Symbol-level code anchors

- `inf_llm/attention/context_manager.py:6` — `CudaCache`
- `inf_llm/attention/stream_llm.py:6` — `stream_llm_forward`
- `benchmark/eval.py:81` — `parse_args`
- `benchmark/infinitebench_eval.py:17` — `normalize_answer`
- `inf_llm/attention/inf_llm.py:5` — `inf_llm_forward`
- `inf_llm/attention/infinite_lm.py:6` — `infinite_lm_forward`
- `inf_llm/attention/origin.py:4` — `origin_forward`
- `inf_llm/attention/rope.py:4` — `RotaryEmbeddingESM`
- `inf_llm/attention/utils.py:4` — `repeat_kv`
- `inf_llm/utils/greedy_search.py:3` — `GreedySearch`
- `inf_llm/attention/dot_production_attention/__init__.py:4` — `get_multi_stage_dot_production_attention`
- `inf_llm/attention/dot_production_attention/base.py:3` — `MultiStageDotProductionAttention`
