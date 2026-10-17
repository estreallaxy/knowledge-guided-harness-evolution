# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Mem2ACTBench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/Mem2ACTBench_small/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/prompts/conversation_example.json` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/extract_tool_pool.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/05_benchmark_normalization.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/03_conv_sort.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/02_extract_facts_conflicts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/01_conversation_builder.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/04_qa_construction.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
