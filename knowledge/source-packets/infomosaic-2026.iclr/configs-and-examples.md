# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README_CN.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/MCP/config/agent_tools.json` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/MCP/config_manager.py` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/MCP/server/BASE-TOOL-Server/configs/common_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/MCP/sse_server/biomcp-main/example_scripts/mcp_integration.py` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/MCP/sse_server/biomcp-main/example_scripts/python_sdk.py` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/MCP/sse_server/biomcp-main/tests/config/test_smithery_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/README_ZH.md` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/configs/web_agent.json` | Dependency, configuration, or usage evidence. |
| `official-code/tool_backends/run_docker.sh` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tool_backends/run_docker.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
