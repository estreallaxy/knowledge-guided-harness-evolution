# Tests and reported results

## Official verification entry points

- `tests/README.md`
- `tests/reliability/README.md`
- `tests/clients/fixtures/lm_3_3_0/README.md`
- `tests/clients/test_prompt_cache.py`
- `tests/streaming/test_react_v2_native_tool_stream.py`
- `tests/teleprompt/test_copro_optimizer.py`
- `tests/teleprompt/test_random_search.py`
- `tests/test_lm15_subtree_updater.py`
- `tests/primitives/test_interpreter_factory_config.py`
- `tests/test_utils/server/litellm_server_config.yaml`
- `tests/adapters/test_tool.py`
- `tests/callback/test_optimizer_callback.py`
- `tests/clients/test_cache.py`
- `tests/evaluate/test_auto_evaluation.py`
- `tests/evaluate/test_evaluate.py`
- `tests/evaluate/test_metrics.py`
- `tests/flex/test_tools.py`
- `tests/predict/test_decision_prompts.py`
- `tests/primitives/test_sandbox_serializable.py`
- `tests/retrievers/test_colbertv2.py`
- `tests/retrievers/test_embeddings.py`
- `tests/streaming/test_streaming.py`
- `tests/teleprompt/gepa_dummy_lm.json`
- `tests/teleprompt/gepa_dummy_lm_custom_component_selector_custom_instruction_proposer.json`
- `tests/teleprompt/test_bettertogether.py`
- `tests/teleprompt/test_bootstrap.py`
- `tests/teleprompt/test_bootstrap_finetune.py`
- `tests/teleprompt/test_bootstrap_trace.py`
- `tests/teleprompt/test_ensemble.py`
- `tests/teleprompt/test_finetune.py`

## Published result anchors

- p. 7: Table 1: Results with in-context learning on GSM8K math word problems. Each row represents
- p. 9: Table 2: Results with in-context learning on HotPotQA. We report answer exact match (Ans) and

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/stanfordnlp/dspy at `c85fae85e5dbf504d7fe46042cd88b93e3787023` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
