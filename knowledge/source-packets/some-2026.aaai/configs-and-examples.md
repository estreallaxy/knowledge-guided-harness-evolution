# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/qwen_agent/tools/retrieval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/qwen_agent/tools/web_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/qwen_agent/tools/python_executor.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/qwen_agent/tools/search_tools/front_page_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/qwen_agent/tools/search_tools/hybrid_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/qwen_agent/tools/search_tools/vector_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/qwen_agent/tools/search_tools/base_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/qwen_agent/tools/search_tools/keyword_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/qwen_agent/agents/dialogue_retrieval_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tools/topic_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tools/user_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tools/data_retrieve.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
