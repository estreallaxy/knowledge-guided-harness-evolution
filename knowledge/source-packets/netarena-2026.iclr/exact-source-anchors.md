# Exact source anchors

## Selected mechanism

Generate dynamic network-operation tasks and evaluate correctness, safety, and latency in emulated environments.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | system |
| Results and ablations | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/netarena/agent_client.py:40` | `PromptType` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/netarena/agent_client.py:51` | `AgentClientConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/netarena/agent_client.py:71` | `AgentClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-route/old_code/prompt_agent.py:102` | `BasePromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-route/old_code/prompt_agent.py:141` | `ZeroShot_CoT_PromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-route/old_code/prompt_agent.py:172` | `FewShot_Basic_PromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-k8s/old_code/prompt_agent.py:85` | `BasePromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-k8s/old_code/prompt_agent.py:119` | `ZeroShot_CoT_PromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-k8s/old_code/prompt_agent.py:156` | `FewShot_Basic_PromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-malt/old_code/prompt_agent.py:86` | `BasePromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-malt/old_code/prompt_agent.py:161` | `ZeroShot_CoT_PromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-malt/old_code/prompt_agent.py:210` | `FewShot_Basic_PromptAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-route/safety_check.py:3` | `safety_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-k8s/run_workflow.py:27` | `K8sConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-k8s/run_workflow.py:48` | `deploy_k8s_cluster` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-k8s/run_workflow.py:70` | `run_error_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-route/green_agent/route_agent.py:38` | `EvalRequest` | Pinned implementation entry for the selected mechanism. |
| `official-code/app-route/green_agent/route_agent.py:43` | `RouteEvalAgent` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `525ca6a80fce5a8faef508b70137fbd0513a85cb`. Paper page numbers refer to the fixed local proceedings PDF.
