# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/context7-mcp/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/context7-mcp/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/context7-mcp/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/context7-mcp/eslint.config.js` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/context7-mcp/tsconfig.json` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/mcp-google-map/src/config.ts` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/mcp-server-nationalparks/src/config.ts` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/paper-search-mcp/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/paper-search-mcp/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/paper-search-mcp/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/mcp_servers/paper-search-mcp/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agent/execution_context.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent/executor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/metmuseum-mcp/src/tools/SearchMuseumObjectsTool.ts` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/mcp-google-map/src/tools/maps/searchNearby.ts` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_length.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_volume.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_temperature.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_area.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_computer.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_pressure.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_power.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_force.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
