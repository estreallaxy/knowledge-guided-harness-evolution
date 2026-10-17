# Exact source anchors

## Selected mechanism

We introduce TRACER, a trajectory-level uncertainty metric for dual-control Tool-Agent-User interaction.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | method |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4. Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/tau2/environment/toolkit.py:17` | `ToolKitType` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/toolkit.py:41` | `ToolType` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/toolkit.py:50` | `is_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/tool.py:17` | `BaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/tool.py:38` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/tool.py:185` | `as_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/orchestrator/environment_manager.py:14` | `StartEnvironmentRequest` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/orchestrator/environment_manager.py:19` | `StatusResponse` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/orchestrator/environment_manager.py:23` | `EnvironmentResponse` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/utils/interface_agent.py:33` | `InterfaceAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/utils/interface_agent.py:97` | `get_interface_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/utils/interface_agent.py:102` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/metrics/agent_metrics.py:11` | `is_successful` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/metrics/agent_metrics.py:18` | `AgentMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/metrics/agent_metrics.py:33` | `pass_hat_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/db.py:7` | `DB` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/db.py:37` | `get_db_json_schema` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/server.py:12` | `EnvironmentServer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `dba3de264c886aa98af1fa2779dd49f7aed8cf92`. Paper page numbers refer to the fixed local proceedings PDF.
