# Exact source anchors

## Selected mechanism

We propose COBA ( CO mponent-based B enchmark A uditing), an automated pipeline for diagnosing and filtering validity issues in agent benchmarks.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | design |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | results |
| Limitations or failure conditions | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 5. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tau2-bench/src/tau2/environment/toolkit.py:17` | `ToolKitType` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/environment/toolkit.py:41` | `ToolType` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/environment/toolkit.py:50` | `is_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/environment/tool.py:17` | `BaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/environment/tool.py:38` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/environment/tool.py:185` | `as_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/orchestrator/environment_manager.py:14` | `StartEnvironmentRequest` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/orchestrator/environment_manager.py:19` | `StatusResponse` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/orchestrator/environment_manager.py:23` | `EnvironmentResponse` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/environment/utils/interface_agent.py:33` | `InterfaceAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/environment/utils/interface_agent.py:104` | `get_interface_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/environment/utils/interface_agent.py:109` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/metrics/agent_metrics.py:11` | `is_successful` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/metrics/agent_metrics.py:18` | `AgentMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau2-bench/src/tau2/metrics/agent_metrics.py:33` | `pass_hat_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau-bench/tau_bench/agents/tool_calling_agent.py:19` | `ToolCallingAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau-bench/tau_bench/agents/tool_calling_agent.py:333` | `message_to_action` | Pinned implementation entry for the selected mechanism. |
| `official-code/tau-bench/tau_bench/envs_fixed/airline/tools/transfer_to_human_agents.py:7` | `TransferToHumanAgents` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `0f9eac1c1a376a411ad807bd974555055f08e6c5`. Paper page numbers refer to the fixed local proceedings PDF.
