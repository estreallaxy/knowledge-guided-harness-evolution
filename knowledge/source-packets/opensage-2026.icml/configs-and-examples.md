# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/agent_library/agents/devops_gym_agent/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/harbor_agent/config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/poc_agent_dynamic_tools/config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/poc_agent_static_tools/config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/repo_maintainer_agent/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/swebenchpro_agent/docker_config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/swebenchpro_agent/docker_no_neo4j_config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/swebenchpro_agent/nitrobox_config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/swebenchpro_agent/nitrobox_overlayfs_config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/vul_agent_static_tools/cybergym_vul_detect_config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/agent_library/agents/vul_agent_static_tools/vul_detect_config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/src/opensage/toolbox/sandbox_requirements.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tests/unit/tests/bash_tools/retrieval/test_search_symbol.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/opensage/bash_tools/swe_agent/diff_state/scripts/_state_diff_state.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/unit/tests/agents/test_opensage_agent_prompt.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/unit/tests/agents/test_opensage_mcp_toolset.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/unit/tests/tools/test_fuzzy_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/opensage/bash_tools/retrieval/common_utils/neo4j_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/opensage/bash_tools/retrieval/list-functions/scripts/list_functions.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/common_tools/retrieval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
