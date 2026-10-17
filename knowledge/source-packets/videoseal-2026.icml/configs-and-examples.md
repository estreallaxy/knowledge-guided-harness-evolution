# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/rllm/environments/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/rllm/environments/base/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/rllm/environments/base/base_env.py` | Dependency, configuration, or usage evidence. |
| `official-code/rllm/environments/base/single_turn_env.py` | Dependency, configuration, or usage evidence. |
| `official-code/rllm/environments/env_utils.py` | Dependency, configuration, or usage evidence. |
| `official-code/rllm/environments/swe/cache_images_k8.py` | Dependency, configuration, or usage evidence. |
| `official-code/rllm/environments/tools/mcp_env.py` | Dependency, configuration, or usage evidence. |
| `official-code/rllm/environments/tools/tool_env.py` | Dependency, configuration, or usage evidence. |
| `official-code/verl/utils/reward_score/prime_code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/verl/workers/config/reward_model.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/rllm/environments/tools/mcp_env.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/rllm/environments/tools/tool_env.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/verl/utils/reward_score/search_r1_like_qa_em.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/rllm/agents/video_system_prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/verl/tools/mcp_search_tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/rllm/agents/tool_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/verl/tools/search_tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/videoseal/agents/tool_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/videoseal/utils/agent/tool_schema.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
