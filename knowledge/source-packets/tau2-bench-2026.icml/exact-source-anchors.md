# Exact source anchors

## Selected mechanism

In order to address this gap, we introduce $\tau^2$-bench, with four key contributions: (1) A novel Telecom dual-control domain modeled as a Dec-POMDP, where both agent and user make use of tools to act in a shared, dynamic environment that tests both agent coordination and communication; (2) A compositional task generator that programmatically creates diverse, verifiable tasks from atomic components, ensuring domain coverage and controlled complexity; (3) A reliable user simulator tightly coupled with the environment, whose behavior is constrained by tools and observable states, improving simulation fidelity; (4) Fine-grained analysis of agent performance through multiple ablations includin

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.26; `paper/paper-icml2026.txt` marker `===== PDF p.26 =====` | method |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.2. Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/tau2/environment/tool.py:17` | `BaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/tool.py:38` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/tool.py:185` | `as_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/orchestrator/environment_manager.py:14` | `StartEnvironmentRequest` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/orchestrator/environment_manager.py:19` | `StatusResponse` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/orchestrator/environment_manager.py:23` | `EnvironmentResponse` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/toolkit.py:19` | `ToolKitType` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/toolkit.py:43` | `ToolType` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/toolkit.py:64` | `is_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/utils/interface_agent.py:33` | `InterfaceAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/utils/interface_agent.py:99` | `get_interface_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/environment/utils/interface_agent.py:104` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/metrics/agent_metrics.py:12` | `is_successful` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/metrics/agent_metrics.py:19` | `AgentMetrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/metrics/agent_metrics.py:113` | `pass_hat_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/domains/banking_knowledge/retrieval_toolkits.py:34` | `KnowledgeToolsPlain` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/domains/banking_knowledge/retrieval_toolkits.py:43` | `KnowledgeToolsWithKBSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tau2/domains/banking_knowledge/retrieval_toolkits.py:54` | `KnowledgeToolsWithGrep` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `96a3ef92329baf908ffe9dfe188cea34e8701d2a`. Paper page numbers refer to the fixed local proceedings PDF.
