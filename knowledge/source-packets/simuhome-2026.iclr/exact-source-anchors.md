# Exact source anchors

## Selected mechanism

Use a time-accelerated, stateful smart-home simulator to pre-validate schedules and observe delayed environmental effects.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.25; `paper/paper-iclr2026.txt` marker `===== PDF p.25 =====` | System |
| Experimental setup | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Experimental Setup |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/agents/tools.py:23` | `load_docs` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/tools.py:44` | `load_faiss` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/tools.py:70` | `ToolConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/memory/hi_memory.py:7` | `HiMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cli/episode_evaluator.py:21` | `ProgressEvent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cli/episode_evaluator.py:37` | `EvaluationStats` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/cli/episode_evaluator.py:79` | `_contains_any_marker` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/types.py:7` | `ChatMessage` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/__init__.py:7` | `_ensure_langchain_pydantic_v1` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/strategies/__init__.py:8` | `create_agent_strategy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/providers/base.py:9` | `_normalize_messages` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/providers/base.py:26` | `LLMProvider` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/providers/base.py:38` | `NonRetryableLLMError` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/strategies/base.py:9` | `AgentExecutionError` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/strategies/base.py:14` | `AgentStep` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/strategies/base.py:32` | `ToolInvocation` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/providers/openai_provider.py:23` | `_env_bool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/providers/openai_provider.py:30` | `_extract_error_message` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `83d28837b69f0cbf1bc02ed5334cb8b561a9d54d`. Paper page numbers refer to the fixed local proceedings PDF.
