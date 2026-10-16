# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/generator_requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/hnswlib/examples/python/example_search.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements-build.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements-dev.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements-neuron.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements-rocm.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/retriever_requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/tests/prompts/example.txt` | Dependency, configuration, or usage evidence. |
| `official-code/vllm/model_executor/layers/fused_moe/configs/README` | Dependency, configuration, or usage evidence. |
| `official-code/vllm/model_executor/layers/quantization/base_config.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tests/core/test_scheduler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/metrics/test_metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/spec_decode/test_metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/setup.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vllm/core/scheduler.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vllm/entrypoints/searchagent-x.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/core/utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
