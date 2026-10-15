# Exact source anchors

## Selected mechanism

Estimate token saliency from normalized attention, assign mixed 2/4-bit KV precision, and periodically recompress during decoding.

## Paper anchors

- p. 2: approach aligns with the observation that a minority of tokens contribute the majority of attention
- p. 3: approach. Typically, a finer quantization granularity involves the independent quantization of smaller
- p. 4: 4 Method
- p. 4: results in 2bl quantization parameters, while groupwise quantization would yield 2bhld n quantization
- p. 7: approach that combines recent tokens with randomly selected tokens emerges as the most effective.
- p. 7: 5 Experiment
- p. 7: 5.1 Implementation Details
- p. 8: 5.2.1 Evaluation on GSM8k
- p. 8: 5.3 Evaluation on HumanEval
- p. 9: 5.3.1 Evaluation on Line Retrival
- p. 10: framework for compressing KV cache. To commence, we introduce a channel-separable quantization
- p. 10: Limitations and Broader Impacts. While ZipCache presents promising advancements in KV cache

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.py`
- `zipcache/models/modeling_llama.py`
- `zipcache/models/modeling_mistral.py`
- `zipcache/models/CompressUtils/__init__.py`
- `zipcache/models/CompressUtils/compress_class.py`
- `zipcache/models/CompressUtils/compress_function.py`
- `zipcache_generation_demo.py`
- `zipcache/__init__.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. ZipCache is an inference-time quantization policy with no fine-tuning. Main-track experiments report accuracy, memory, and latency; code provides quantizers, saliency approximation, and evaluation.

## Symbol-level code anchors

- `zipcache/models/modeling_llama.py:77` — `detect_infnan`
- `zipcache/models/modeling_mistral.py:77` — `MistralRMSNorm`
- `zipcache/models/CompressUtils/compress_class.py:95` — `detect_infnan`
- `zipcache/models/CompressUtils/compress_function.py:4` — `transfer_8bit_to_2bit_batchwise`
