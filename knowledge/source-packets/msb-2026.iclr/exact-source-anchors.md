# Exact source anchors

## Selected mechanism

Test Model Context Protocol agents against tool, transport, permission, and data-flow attacks in a controlled harness.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.29; `paper/paper-iclr2026.txt` marker `===== PDF p.29 =====` | System |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/mcp_use/agents/prompts/system_prompt_builder.py:5` | `generate_tool_descriptions` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/agents/prompts/system_prompt_builder.py:86` | `build_system_prompt_content` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/agents/prompts/system_prompt_builder.py:118` | `create_system_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/search_tools.py:13` | `ToolSearchInput` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/search_tools.py:23` | `SearchToolsTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/search_tools.py:58` | `ToolSearchEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:24` | `structured_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:53` | `check_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:196` | `get_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/agents/base.py:13` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/setup.py:6` | `replace_content` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/agents/mcpagent.py:38` | `MCPAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/base_tool.py:6` | `MCPServerTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/get_active_server.py:8` | `CurrentServerInput` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/get_active_server.py:14` | `GetActiveServerTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/disconnect_server.py:10` | `DisconnectServerInput` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/disconnect_server.py:16` | `DisconnectServerTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_use/managers/tools/list_servers_tool.py:10` | `listServersInput` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c1d6a70171e4d2c44c87a2ae909d13df00c6aa8d`. Paper page numbers refer to the fixed local proceedings PDF.
