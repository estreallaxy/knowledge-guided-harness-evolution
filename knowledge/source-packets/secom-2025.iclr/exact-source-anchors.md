# Exact source anchors

## Selected mechanism

Segment conversations by topical coherence, compress each memory unit to remove retrieval noise, and retrieve via BM25/vector backends through one memory API.

## Paper anchors

- p. 5: Implementation Details We use GPT-35-Turbo for response generation in our main exper-
- p. 5: evaluation across different LLMs. We employ zero-shot segmentation for QA benchmarks and
- p. 7: Ablation Study on Granularity of Memory Units Figure 2b, Figure 2c, and Table 3 have clearly
- p. 7: Ablation Study on Compression based Memory Denoising As shown in Table 2, removing
- p. 8: method demonstrates a significant performance gain over other baselines, showcasing its good
- p. 8: Evaluation of Conversation Segmentation Model To evaluate the conversation segmentation
- p. 13: evaluation of machine translation. In Proceedings of the 40th annual meeting of the Association
- p. 18: results. The superiority of our S E C OM is also evident on these QA pairs, demonstrating its superior
- p. 21: evaluation is generally consistent with those obtained from automated metrics, confirming the

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `setup.py`
- `.pre-commit-config.yaml`
- `experiment/compress.py`
- `experiment/retrieve.py`
- `experiment/run.sh`
- `secom/configs/bm25.yaml`
- `secom/configs/fast.yaml`
- `secom/configs/mpnet.yaml`
- `example/example.json`
- `experiment/chat.py`
- `experiment/download_data.py`
- `experiment/metrics.py`
- `experiment/segment.py`
- `experiment/utils.py`
- `secom/__init__.py`
- `secom/secom.py`
- `secom/utils.py`
- `secom/version.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Using the released segmentor/compressor at inference requires no optimizer/agent weight update. The paper compares granularities and retrieval accuracy; code exposes build_memory, compress, retrieve, and update_database.

## Symbol-level code anchors

- `experiment/compress.py:21` — `load_data`
- `experiment/retrieve.py:30` — `load_data`
- `experiment/chat.py:36` — `load_data`
- `experiment/metrics.py:15` — `normalize_answer`
- `experiment/segment.py:19` — `load_data`
- `experiment/utils.py:14` — `OpenAILLM`
- `secom/secom.py:18` — `SeCom`
- `secom/utils.py:14` — `OpenAILLM`
