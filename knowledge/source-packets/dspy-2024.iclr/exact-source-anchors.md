# Exact source anchors

## Selected mechanism

Represent an LM workflow as typed declarative modules and compile instructions/demonstrations from execution traces and metrics.

## Paper anchors

- p. 2: framework and programming abstractions for what we call foundation model programming. We
- p. 2: framework (DSP; Khattab et al. 2022).
- p. 8: Results Our results are summarized in Table 1, which includes dev results as well as our evalua-
- p. 9: Results Table 2 summarizes our results: a simple multihop program is the best across all models
- p. 13: framework for deep learning. In Proceedings of workshop on machine learning systems (Learn-

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `tests/README.md`
- `tests/reliability/README.md`
- `dspy/adapters/types/citation.py`
- `dspy/clients/model_metadata/LICENSE`
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

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The prompt/demo compiler is independent of optional fine-tuning. Methods and ablations isolate bootstrapping/teleprompting; the repository exposes module signatures, tracing, optimizers, and evaluators.

## Symbol-level code anchors

- `tests/reliability/README.md:81` — `test_program_with_complex_deeply_nested_output_structure`
- `dspy/adapters/types/citation.py:13` — `Citations`
- `tests/clients/test_prompt_cache.py:12` — `Engine`
- `tests/streaming/test_react_v2_native_tool_stream.py:27` — `ScriptedToolEngine`
- `tests/teleprompt/test_copro_optimizer.py:8` — `simple_metric`
- `tests/teleprompt/test_random_search.py:10` — `SimpleModule`
- `tests/test_lm15_subtree_updater.py:14` — `run`
- `tests/primitives/test_interpreter_factory_config.py:26` — `Doubler`
- `tests/adapters/test_tool.py:14` — `dummy_function`
- `tests/callback/test_optimizer_callback.py:15` — `RecordingCallback`
- `tests/clients/test_cache.py:17` — `DummyResponse`
- `tests/evaluate/test_auto_evaluation.py:7` — `test_semantic_f1_returns_prediction_without_trace`
