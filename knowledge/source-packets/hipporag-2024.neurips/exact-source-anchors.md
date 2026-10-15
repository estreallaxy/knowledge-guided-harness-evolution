# Exact source anchors

## Selected mechanism

Build an entity/relation knowledge graph, seed query entities, and use Personalized PageRank to retrieve associatively connected passages.

## Paper anchors

- p. 6: 3.4 Implementation Details
- p. 6: 4 Results
- p. 10: results on path-following multi-hop QA and promise on path-finding multi-hop QA, as well as its
- p. 13: framework for large language model to reason over structured data. In H. Bouamor,
- p. 24: results in Table 9, we first note that there is a massive difference between end-to-end information
- p. 29: implementation of the PPR algorithm. For BM25, we employ Elastic Search [24]. For multi-step
- p. 32: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 33: implementation details are included in §3 and Appendix H. Additionally, all of our code and
- p. 34: results?
- p. 34: implementation details, including training splits and hyperparameter tuning can be found in
- p. 37: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `requirements.txt`
- `setup.py`
- `reproduce/README.md`
- `src/hipporag/evaluation/README.md`
- `src/hipporag/prompts/templates/README.md`
- `tests/test_hipporag_state_consistency.py`
- `tests/test_openie_extraction.py`
- `tests/integration/run_azure.py`
- `tests/integration/run_gateway.py`
- `tests/integration/run_local.py`
- `tests/integration/run_openai.py`
- `tests/integration/run_transformers.py`
- `tests/integration/run_vector_stores.py`
- `tests/test_bedrock_llm.py`
- `tests/test_bedrock_mantle.py`
- `tests/test_gateway_llm.py`
- `tests/test_openai_sdk_compat.py`
- `tests/test_regressions.py`
- `src/hipporag/evaluation/retrieval_eval.py`
- `main.py`
- `src/hipporag/prompts/templates/triple_extraction.py`
- `tests/integration/_shared.py`
- `src/hipporag/utils/config_utils.py`
- `examples/_shared.py`
- `examples/demo_azure.py`
- `examples/demo_bedrock.py`
- `examples/demo_bedrock_mantle.py`
- `examples/demo_gateway.py`
- `examples/demo_local.py`
- `examples/demo_openai.py`
- `src/hipporag/evaluation/base.py`
- `src/hipporag/evaluation/qa_eval.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The memory/index/retrieval pipeline is non-parametric and works with frozen models. The paper reports multi-hop and single-hop results; the repository includes indexing, graph retrieval, reproduction, and tests.

## Symbol-level code anchors

- `tests/test_hipporag_state_consistency.py:13` — `FakeLLM`
- `tests/test_openie_extraction.py:6` — `TestOpenIEExtraction`
- `tests/integration/run_vector_stores.py:39` — `MockEmbeddingModel`
- `tests/test_bedrock_llm.py:12` — `bedrock_response`
- `tests/test_bedrock_mantle.py:14` — `BedrockMantleLLMTest`
- `tests/test_gateway_llm.py:19` — `fake_response`
- `tests/test_openai_sdk_compat.py:25` — `chat_payload`
- `tests/test_regressions.py:31` — `ConfigurableEmbeddingModel`
- `src/hipporag/evaluation/retrieval_eval.py:16` — `RetrievalRecall`
- `main.py:19` — `get_gold_docs`
- `tests/integration/_shared.py:5` — `run_lifecycle`
- `src/hipporag/utils/config_utils.py:15` — `BaseConfig`
