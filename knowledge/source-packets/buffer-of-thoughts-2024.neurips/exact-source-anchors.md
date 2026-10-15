# Exact source anchors

## Selected mechanism

Store abstract thought templates in a meta-buffer, retrieve and instantiate one for a new task, and let a buffer manager update reusable templates.

## Paper anchors

- p. 4: approach based on the method described. Here is def combine_elements(element1, element2):
- p. 4: approach based on the method described. Here
- p. 7: Implementation and Baselines For the fair comparisons with previous methods, we use GPT-4
- p. 7: method achieves an astonishing 79.4% accuracy improvement in Game of 24, and compared to ToT,
- p. 10: Ablation study of buffer-manager -- Accuracy
- p. 14: Ablation study of problem-distiller
- p. 14: Ablation study of meta-buffer
- p. 15: Ablation study of buffer-manager -- Time
- p. 19: approach based on the method described. Here is the structured template for solving such
- p. 21: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 23: results?
- p. 26: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `test_templates.py`
- `run_benchmarks.py`
- `lightrag/prompt.py`
- `bot_pipeline.py`
- `inference.py`
- `meta_buffer.py`
- `meta_buffer_utilis.py`
- `validate_results.py`
- `lightrag/__init__.py`
- `lightrag/base.py`
- `lightrag/lightrag.py`
- `lightrag/llm.py`
- `lightrag/operate.py`
- `lightrag/storage.py`
- `lightrag/utils.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The complete mechanism is prompt/retrieval/state based. The paper reports accuracy, robustness, and cost, and the repository implements template retrieval, instantiation, and buffer maintenance.

## Symbol-level code anchors

- `test_templates.py:5` — `find_solution`
- `bot_pipeline.py:11` — `Pipeline`
- `meta_buffer.py:7` — `MetaBuffer`
- `meta_buffer_utilis.py:46` — `extract_and_execute_code`
- `lightrag/base.py:17` — `QueryParam`
- `lightrag/lightrag.py:43` — `always_get_an_event_loop`
- `lightrag/llm.py:42` — `openai_complete_if_cache`
- `lightrag/operate.py:29` — `chunking_by_token_size`
- `lightrag/storage.py:19` — `JsonKVStorage`
- `lightrag/utils.py:21` — `set_logger`
