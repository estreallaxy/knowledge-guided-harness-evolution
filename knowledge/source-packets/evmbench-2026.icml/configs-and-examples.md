# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/project/common/nanoeval/nanoeval/examples/bundled_evals_test.py` | Dependency, configuration, or usage evidence. |
| `official-code/project/common/nanoeval/nanoeval/solvers/computer_tasks/demo/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/project/common/nanoeval/nanoeval/solvers/computer_tasks/demo/runtime.py` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/evmbench/agents/claude/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/evmbench/agents/codex/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/evmbench/agents/gemini/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/evmbench/agents/human/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/evmbench/agents/opencode/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/init/src/attack.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/init/src/config.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/init/src/grade.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/init/src/setup.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/init/src/txs.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/reentrancy/src/attack.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/reentrancy/src/config.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/reentrancy/src/grade.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/reentrancy/src/setup.rs` | Dependency, configuration, or usage evidence. |
| `official-code/project/evmbench/ploit/examples/reentrancy/src/txs.rs` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/project/evmbench/evmbench/agents/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/project/paperbench/paperbench/judge/judge_eval/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
