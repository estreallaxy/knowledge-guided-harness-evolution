# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/config/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/config/benchmark_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/src/config/config_loader.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/mcp_configs/lark-mcp.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/mcp_configs/notion.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/mcp_configs/obsidian.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/mcp_configs/reddit.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/mcp_configs/slack.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/mcp_configs/universal-email.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/mcp_configs/wecome.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/mcp_configs/xiaohongshu.json` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
