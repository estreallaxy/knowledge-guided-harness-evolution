# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/agent/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/agent/base_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/agent/text_dagger_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/agent/text_dqn_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/agent/vision_dagger_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/config/rewards.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/controller/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/controller/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/controller/mrcnn.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/controller/mrcnn_astar.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/controller/oracle.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/controller/oracle_astar.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/coco_eval.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/coco_utils.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/engine.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/group_by_aspect_ratio.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/mrcnn.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/transforms.py` | Dependency, configuration, or usage evidence. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/detector/utils.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/eval/evaluate_dagger.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/eval/evaluate_dqn.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent_system/environments/env_package/alfworld/alfworld/agents/eval/evaluate_vision_dagger.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
