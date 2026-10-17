# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE.txt` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/coact/autogen/coding/docker_commandline_code_executor.py` | Dependency, configuration, or usage evidence. |
| `official-code/desktop_env/evaluators/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_examples/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_examples/test_1.json` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_examples/test_nogdrive_norobot_nogimp_noOS_nothunderbird_novlc_novscode.json` | Dependency, configuration, or usage evidence. |
| `official-code/evaluation_examples/test_small.json` | Dependency, configuration, or usage evidence. |
| `official-code/how_to_license.md` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/coact/autogen/coding/docker_commandline_code_executor.py` | Dependency, configuration, or usage evidence. |
| `official-code/mm_agents/coact/autogen/llm_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/mm_agents/coact/autogen/tools/experimental/duckduckgo/duckduckgo_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mm_agents/coact/autogen/tools/experimental/google_search/google_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mm_agents/coact/autogen/tools/experimental/web_search_preview/web_search_preview.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mm_agents/coact/autogen/tools/experimental/google_search/youtube_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mm_agents/coact/autogen/tools/experimental/tavily/tavily_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mm_agents/coact/autogen/tools/experimental/perplexity/perplexity_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mm_agents/coact/autogen/tools/experimental/deep_research/deep_research.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
