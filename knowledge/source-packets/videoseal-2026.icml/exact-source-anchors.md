# Exact source anchors

## Selected mechanism

Retain the decoupled planner-inspector architecture, temporal and semantic groundedness diagnostics, pixel-level verification gate, and interpretable search trajectories; exclude outcome-only training.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 5. Experiments |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 5.3. Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/rllm/environments/tools/mcp_env.py:17` | `MCPConnectionManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/rllm/environments/tools/mcp_env.py:173` | `MCPEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/rllm/environments/tools/tool_env.py:14` | `ToolEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl/utils/reward_score/search_r1_like_qa_em.py:23` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl/utils/reward_score/search_r1_like_qa_em.py:40` | `em_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl/utils/reward_score/search_r1_like_qa_em.py:53` | `subem_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/rllm/agents/video_system_prompts.py:13` | `build_toolagent_sys_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl/tools/mcp_search_tool.py:28` | `MCPSearchTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/rllm/agents/tool_agent.py:17` | `_sec_to_hhmmss` | Pinned implementation entry for the selected mechanism. |
| `official-code/rllm/agents/tool_agent.py:25` | `_extract_video_duration_sec` | Pinned implementation entry for the selected mechanism. |
| `official-code/rllm/agents/tool_agent.py:49` | `ToolAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl/tools/search_tool.py:41` | `PoolMode` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl/tools/search_tool.py:49` | `TokenBucketWorker` | Pinned implementation entry for the selected mechanism. |
| `official-code/verl/tools/search_tool.py:74` | `SearchExecutionWorker` | Pinned implementation entry for the selected mechanism. |
| `official-code/videoseal/agents/tool_agent.py:26` | `_is_local_or_private_api_base` | Pinned implementation entry for the selected mechanism. |
| `official-code/videoseal/agents/tool_agent.py:46` | `_bool_env_or_default` | Pinned implementation entry for the selected mechanism. |
| `official-code/videoseal/agents/tool_agent.py:52` | `_system_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/videoseal/utils/agent/tool_schema.py:20` | `sanitize_args_against_schema` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d6561c9ab5defacdfe3c28e6a631a2c34a6953aa`. Paper page numbers refer to the fixed local proceedings PDF.
