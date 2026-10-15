# Tests and reported results

## Official verification entry points

- `src/hipporag/evaluation/README.md`
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
- `tests/integration/_shared.py`
- `src/hipporag/evaluation/base.py`
- `src/hipporag/evaluation/qa_eval.py`
- `src/hipporag/utils/eval_utils.py`

## Published result anchors

- p. 5: Table 1: Retrieval corpora and extracted KG statistics for each of our 1,000 question dev sets.
- p. 6: Table 2: Single-step retrieval performance. HippoRAG outperforms all baselines on MuSiQue and
- p. 6: Table 3: Multi-step retrieval performance. Combining HippoRAG with standard multi-step retrieval
- p. 7: Table 4: QA performance. HippoRAG’s QA improvements correlate with its retrieval improvements
- p. 7: Table 5: Dissecting HippoRAG. To understand what makes it work well, we replace its OpenIE
- p. 8: Table 6: All-Recall metric. We measure the percentage of queries for which all supporting passages
- p. 8: Table 7: Multi-hop question types. We show example results for different approaches on path-finding
- p. 23: Table 8: Knowledge graph statistics using different OpenIE methods.
- p. 24: Table 9: Intrinsic OpenIE evaluation using the CaRB [6] framework on 20 annotated passages.
- p. 25: Table 10: Ranking result examples for different approaches on several path-finding multi-hop

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2024 |
| Official open-source implementation | https://github.com/OSU-NLP-Group/HippoRAG at `d5c8329422e0a0b834a15874545cb6a74b4f9b26` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
