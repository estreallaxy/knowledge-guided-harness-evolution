# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/examples/datagen/harbor/adapters/financeagent/template/environment/edgar_search.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/adapters/financeagent/template/environment/google_search.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/adapters/financeagent/template/environment/retrieve_information.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/cli/template-adapter/template/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/cli/template-task/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/docker-compose-base.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/docker-compose-build.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/docker-compose-no-network.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/docker-compose-prebuilt.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/docker.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/datagen/harbor/src/harbor/environments/docker/image_cache.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference/OpenHands/openhands/agenthub/codeact_agent/tools/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference/OpenHands/openhands/agenthub/codeact_agent/tools/prompt.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference/OpenHands/openhands/agenthub/codeact_agent/tools/security_utils.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference/OpenHands/openhands/agenthub/loc_agent/tools/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference/OpenHands/openhands/agenthub/loc_agent/tools/search_content.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference/OpenHands/openhands/agenthub/readonly_agent/tools/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference/OpenHands/openhands/runtime/plugins/agent_skills/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/examples/inference/OpenHands/openhands/runtime/plugins/agent_skills/file_editor/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/ThunderAgent/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
