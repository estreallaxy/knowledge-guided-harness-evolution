# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/mas/aflow/benchmarks/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/mas/aflow/config/config2.example.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/mas/dylan/code/demo/prompt_lib.py` | Dependency, configuration, or usage evidence. |
| `official-code/mas/maas/config/config2.example.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/mas/maas/examples/maas/config2.example.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/mas/maas/maas/configs/search_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/mas/maas/maas/ext/maas/benchmark/experiment_configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/mas/maas/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/mas_proceval/config_example.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/mas/maas/maas/tools/search_engine_meilisearch.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/web_search_tool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/search_engine_ddg.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/search_engine_bing.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/search_engine_googleapi.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/search_engine_serpapi.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/search_engine_serper.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/prompt_writer.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/search_engine.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/tool_data_type.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/mas/maas/maas/tools/translator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
