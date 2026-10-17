# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/docker/agents/goose/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/docker/agents/goose/add_recipe_prompt.py` | Dependency, configuration, or usage evidence. |
| `official-code/docker/agents/goose/config-template.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/docker/agents/goose/docker-compose.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/docker/agents/goose/entrypoint.sh` | Dependency, configuration, or usage evidence. |
| `official-code/docker/agents/goose/recipe-template.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/abstract_installed_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/aider/aider-setup.sh` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/aider/aider_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/claude_code/claude_code_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/codex/codex_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/cursor_cli/cursor-cli-setup.sh` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/cursor_cli/cursor_cli_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/dgm/dgm_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/gemini_cli/gemini_cli_agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/goose/goose-setup.sh` | Dependency, configuration, or usage evidence. |
| `official-code/fceval/agents/installed_agents/goose/goose_agent.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tests/runtime/test_installed_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/docker/agents/goose/add_recipe_prompt.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/abstract_installed_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/grok_cli/grok_cli_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/cursor_cli/cursor_cli_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/codex/codex_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tests/unit/agents/installed_agents/test_template_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/mini_swe_agent/mini_swe_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/gemini_cli/gemini_cli_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/qwen_code/qwen_code.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/aider/aider_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fceval/agents/installed_agents/goose/goose_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
