# Exact source anchors

## Selected mechanism

Phase/subtask chat chain, instructor–assistant role pairs, communicative dehallucination, and executable review/test feedback. Uses prompted agents without model training.

## Paper anchors

- p. 4: approach continues until all subtasks are com- to sustain the continuity of the dialogue within a
- p. 5: 4 Evaluation ent aspects of coding hallucinations to evaluate the
- p. 6: Method Paradigm Completeness Executability Consistency Quality
- p. 6: Method Evaluator Baseline Wins ChatDev Wins Draw Method Duration (s) #Tokens #Files #Lines
- p. 6: Implementation Details We divided software
- p. 7: 4.2 Ablation Study
- p. 8: Method Not Implemented
- p. 9: 6 Limitations should aim to enhance agent capabilities with fewer

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README-zh.md`
- `README.md`
- `package.json`
- `pyproject.toml`
- `requirements.txt`
- `frontend/package.json`
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
- `workflow/graph_context.py`
- `entity/graph_config.py`
- `server/config_schema_router.py`
- `tests/test_mem0_memory.py`
- `tests/test_memory_embedding_consistency.py`
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

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Phase/subtask chat chain, instructor–assistant role pairs, communicative dehallucination, and executable review/test feedback. Uses prompted agents without model training.

## Symbol-level code anchors

- `workflow/runtime/runtime_context.py:16` — `RuntimeContext`
- `runtime/node/agent/memory/blackboard_memory.py:19` — `BlackboardMemory`
- `runtime/node/agent/memory/builtin_stores.py:51` — `MemoryFactory`
- `runtime/node/agent/memory/embedding.py:18` — `EmbeddingBase`
- `runtime/node/agent/memory/file_memory.py:27` — `FileMemory`
- `runtime/node/agent/memory/mem0_memory.py:41` — `Mem0Memory`
- `runtime/node/agent/memory/memory_base.py:15` — `MemoryContentSnapshot`
- `runtime/node/agent/memory/registry.py:16` — `MemoryStoreRegistration`
- `runtime/node/agent/memory/simple_memory.py:22` — `SimpleMemory`
- `runtime/node/agent/thinking/self_reflection.py:10` — `SelfReflectionThinkingManager`
- `runtime/node/agent/tool/tool_manager.py:38` — `ToolManager`
- `workflow/graph_context.py:15` — `GraphContext`
