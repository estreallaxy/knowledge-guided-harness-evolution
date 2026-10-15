# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `requirements.txt`
- `workflow/runtime/runtime_context.py`
- `runtime/node/agent/memory/__init__.py`
- `runtime/node/agent/memory/blackboard_memory.py`
- `runtime/node/agent/memory/builtin_stores.py`
- `runtime/node/agent/memory/embedding.py`
- `runtime/node/agent/memory/file_memory.py`
- `runtime/node/agent/memory/mem0_memory.py`
- `runtime/node/agent/memory/memory_base.py`
- `runtime/node/agent/memory/registry.py`
- `runtime/node/agent/memory/simple_memory.py`
- `runtime/node/agent/thinking/self_reflection.py`
- `runtime/node/agent/tool/__init__.py`
- `runtime/node/agent/tool/tool_manager.py`
- `entity/graph_config.py`
- `server/config_schema_router.py`
- `tests/test_server_main_reload.py`
- `workflow/runtime/__init__.py`
- `workflow/runtime/execution_strategy.py`
- `workflow/runtime/result_archiver.py`
- `workflow/runtime/runtime_builder.py`
- `runtime/node/agent/__init__.py`
- `runtime/node/executor/agent_executor.py`
- `runtime/node/executor/subgraph_executor.py`
- `runtime/node/agent/providers/__init__.py`
- `runtime/node/agent/providers/base.py`
- `runtime/node/agent/providers/builtin_providers.py`
- `runtime/node/agent/providers/gemini_provider.py`
- `runtime/node/agent/providers/openai_provider.py`

## Upstream command excerpts

```text
uv sync
```

```text
cd frontend && npm install
```

```text
make dev
```

```text
# Run from the project root
    uv run python server_main.py --port 6400 --reload
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
