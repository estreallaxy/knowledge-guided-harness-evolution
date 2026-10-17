# Exact source anchors

## Selected mechanism

Connect agents to live MCP servers and evaluate multi-step, cross-tool plans with executable task graders.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | framework |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | results |
| Limitations or failure conditions | PDF p.15; `paper/paper-iclr2026.txt` marker `===== PDF p.15 =====` | discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent/execution_context.py:14` | `ExecutionContext` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/executor.py:23` | `TaskExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/metmuseum-mcp/src/tools/SearchMuseumObjectsTool.ts:8` | `SearchMuseumObjectsTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/mcp-google-map/src/tools/maps/searchNearby.ts:21` | `ACTION` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_length.py:6` | `TestLengthConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_volume.py:6` | `TestVolumeConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_temperature.py:6` | `TestTemperatureConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_area.py:6` | `TestAreaConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_computer.py:6` | `TestComputerConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_pressure.py:6` | `TestPressureConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_power.py:6` | `TestPowerConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_force.py:6` | `TestForceConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_energy.py:6` | `TestEnergyConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_speed.py:6` | `TestSpeedConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_mass.py:6` | `TestMassConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/unit-converter-mcp/tests/tools/test_time.py:6` | `TestTimeConversion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/biomcp/src/biomcp/metrics_handler.py:10` | `get_performance_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/mcp_servers/biomcp/src/biomcp/metrics_handler.py:51` | `_format_summary` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7a8eaeae83a842a2949080acc5473f65e1569daf`. Paper page numbers refer to the fixed local proceedings PDF.
