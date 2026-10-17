# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/MAS/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/MAS/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/setup.sh` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/MAS/epc_aw/tools/web_search/google_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/MAS/epc_aw/tools/google_search/local_google_scraper.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/MAS/epc_aw/tools/wikipedia_search/web_rag.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/MAS/epc_aw/tools/google_search/tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/MAS/epc_aw/tools/wikipedia_search/tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/MAS/epc_aw/tools/web_search/tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/test/calculate_score_unified.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/MAS/epc_aw/tools/base.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/MAS/epc_aw/tools/base_generator/tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
