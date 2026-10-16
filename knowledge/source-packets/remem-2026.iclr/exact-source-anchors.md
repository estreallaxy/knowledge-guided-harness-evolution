# Exact source anchors

## Selected mechanism

Index experiences as a time-aware hybrid graph and let an agent iteratively retrieve and reason over episodic events.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | framework |
| Results and ablations | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/remem/agent/tools/find_gist_contexts_tool.py:6` | `FindGistContextsTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/tools/semantic_retrieve_tool.py:7` | `SemanticRetrieveTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/tools/lexical_retrieve_tool.py:6` | `LexicalRetrieveTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/tools/find_entity_contexts_tool.py:7` | `FindEntityContextsTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/graph_agent.py:8` | `AgentState` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/graph_agent.py:47` | `GraphAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/strategies/tool_strategy.py:13` | `RetrievalResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/strategies/tool_strategy.py:22` | `ToolStrategy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/tools/output_answer_tool.py:5` | `OutputAnswerTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/strategies/flexible_tools_strategy.py:7` | `FlexibleToolsStrategy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/strategies/fixed_tools_strategy.py:7` | `FixedToolsStrategy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/tools/tool_selector.py:12` | `ToolSelector` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/tools/base_tool.py:21` | `dates_overlap` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/tools/base_tool.py:90` | `ToolType` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/tools/base_tool.py:101` | `ToolContext` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/agent_config.py:13` | `SearchStrategy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/agent_config.py:22` | `ReasoningMode` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/remem/agent/agent_config.py:31` | `AgentConfig` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d87840be922c9815a3c97ec24d9c25e4af5c295a`. Paper page numbers refer to the fixed local proceedings PDF.
