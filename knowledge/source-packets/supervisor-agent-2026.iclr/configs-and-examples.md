# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/run.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/run_gaia.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/cookies.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/gaia_scorer.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/mdconvert.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/reformulator.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/run_agents.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/text_inspector_tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/text_web_browser.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/visual_qa.py` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/smolagents_SMAS/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/smolagents_SMAS/examples/open_deep_research/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/smolagents_SMAS/examples/open_deep_research/run_gaia.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/run_agents.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/smolagents_SMAS/src/smolagents/cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
