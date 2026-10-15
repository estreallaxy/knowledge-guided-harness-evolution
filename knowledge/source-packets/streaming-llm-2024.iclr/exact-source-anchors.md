# Exact source anchors

## Selected mechanism

Retain initial attention-sink tokens plus a rolling recent-token window to support stable unbounded streaming inference.

## Paper anchors

- p. 15: Limitations. While StreamingLLM improves the efficiency of LLMs in streaming contexts, it
- p. 16: approach bears a resemblance to our methodology. However, our work uncovers the “attention sink"

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `setup.py`
- `examples/run_streaming_llama.py`
- `streaming_llm/kv_cache.py`
- `examples/eval_long_ppl.py`
- `streaming_llm/enable_streaming_llm.py`
- `streaming_llm/utils.py`
- `streaming_llm/pos_shift/modify_falcon.py`
- `streaming_llm/pos_shift/modify_gpt_neox.py`
- `streaming_llm/pos_shift/modify_llama.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The deployed mechanism requires no fine-tuning; the optional pretraining observation is unnecessary. The paper tests million-token streams and code patches supported model attention/KV-cache behavior.

## Symbol-level code anchors

- `examples/run_streaming_llama.py:19` — `greedy_generate`
- `streaming_llm/kv_cache.py:4` — `slice2d`
- `streaming_llm/enable_streaming_llm.py:4` — `enable_streaming_llm`
- `streaming_llm/utils.py:14` — `parse_args`
- `streaming_llm/pos_shift/modify_falcon.py:19` — `falcon_pos_shift_attention_forward`
- `streaming_llm/pos_shift/modify_gpt_neox.py:20` — `apply_rotary_pos_emb_single`
- `streaming_llm/pos_shift/modify_llama.py:21` — `apply_rotary_pos_emb_single`
