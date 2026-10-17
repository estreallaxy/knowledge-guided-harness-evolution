# Exact source anchors

## Selected mechanism

To bridge this critical gap, we introduce MCP-Persona, the first benchmark specifically designed for evaluating agent performance on real-world, personalized MCP tools.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | method |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/mcp_modules/tool_cache.py:18` | `ToolCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/mcp_modules/tool_cache.py:358` | `get_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/mcp_modules/tool_cache.py:385` | `set_cache_instance` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/test_fake_tool_with_real_records.py:46` | `get_safe_tool_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/test_fake_tool_with_real_records.py:51` | `get_mcp_name_from_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/test_fake_tool_with_real_records.py:56` | `get_mcp_configs_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/fake_tool_caller.py:19` | `FakeToolError` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/fake_tool_caller.py:25` | `ToolNotFoundError` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/fake_tool_caller.py:33` | `ToolExecutionError` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/build_fake_tools_batch.py:49` | `get_safe_tool_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/build_fake_tools_batch.py:54` | `get_fake_tool_cache_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/build_fake_tools_batch.py:60` | `save_fake_tool_cache` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/generate_failed_tool_calls.py:39` | `load_mcp_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/generate_failed_tool_calls.py:147` | `connect_mcp` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/generate_failed_tool_calls.py:177` | `load_success_records` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config/config_loader.py:16` | `BenchmarkConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config/config_loader.py:257` | `get_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config/config_loader.py:269` | `get_mcp_timeout` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b510f5a5371c4524a58aeeb679c1ace845603e95`. Paper page numbers refer to the fixed local proceedings PDF.
