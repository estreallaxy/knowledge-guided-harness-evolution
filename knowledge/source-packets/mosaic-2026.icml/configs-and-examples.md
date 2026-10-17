# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/examples/offline_inference/basic/score.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/offline_inference/metrics.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/online_serving/openai_cross_encoder_score.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/online_serving/openai_cross_encoder_score_for_multimodal.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/online_serving/retrieval_augmented_generation_with_langchain.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/online_serving/retrieval_augmented_generation_with_llamaindex.py` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/tools/test_config_validator.py` | Dependency, configuration, or usage evidence. |
| `official-code/tools/ep_kernels/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/tools/ep_kernels/configure_system_drivers.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/ep_kernels/elastic_ep/install_eep_libraries.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/ep_kernels/install_python_libraries.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/install_nixl.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/update-dockerfile-graph.sh` | Dependency, configuration, or usage evidence. |
| `official-code/tools/validate_config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tests/tools/test_config_validator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tools/validate_config.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/core/test_scheduler_encoder_decoder.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/core/test_chunked_prefill_scheduler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/core/test_scheduler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/v1/core/test_scheduler_e2e.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/v1/core/test_async_scheduler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/v1/core/test_single_type_kv_cache_manager.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
