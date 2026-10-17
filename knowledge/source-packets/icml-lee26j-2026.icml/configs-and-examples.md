# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/flash_style_fused_santa_fixed_tile_budgets/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/santa_fused_proportional_tile_budgets/setup.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/tutorial_code/runtime_common.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/santa_fused_proportional_tile_budgets/setup.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tutorial_code/benchmark_longctx.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tutorial_code/compare_outputs.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tutorial_code/env_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tutorial_code/inference_tutorial.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/tutorial_code/hf_generate_bridge.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
