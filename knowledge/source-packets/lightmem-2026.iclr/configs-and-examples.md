# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/src/lightmem/configs/retriever/contextretriever/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/configs/FullContext.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/configs/MemZeroGraph.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/envs/fullcontext_requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/prompts.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/azure_ai_search.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/elasticsearch.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/neptune.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/opensearch.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/redis.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/valkey.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/vertex_ai_vector_search.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/embeddings/configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/graphs/configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/llms/configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/memory/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/vector_stores/configs.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/agentic_memory/retrievers.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/graphs/prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/prompts/stateful.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/prompts/stateless.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/graphs/configs.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/vertex_ai_vector_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/opensearch.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/azure_ai_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/elasticsearch.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
