# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/SScheduler/policy/example_policies.py` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/generative_agents/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/hicache/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/line_retrieval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/scripts/playground/long_context_example.py` | Dependency, configuration, or usage evidence. |
| `official-code/sgl-router/src/config/mod.rs` | Dependency, configuration, or usage evidence. |
| `official-code/sgl-router/src/config/types.rs` | Dependency, configuration, or usage evidence. |
| `official-code/sgl-router/src/config/validation.rs` | Dependency, configuration, or usage evidence. |
| `official-code/sgl-router/src/reasoning_parser/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/sgl-router/src/tokenizer/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/test/srt/configs/deepseek_v3_long_context.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/sgl-router/src/tool_parser/state.rs` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/sgl-router/src/metrics.rs` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/sgl-router/src/tool_parser/tests.rs` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/sgl-router/src/config/validation.rs` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/sgl-router/src/tool_parser/traits.rs` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/sgl-router/src/tool_parser/types.rs` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/sgl-router/src/tool_parser/registry.rs` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
