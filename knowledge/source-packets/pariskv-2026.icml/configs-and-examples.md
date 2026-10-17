# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config/DeepSeek-R1-Distill-Llama-8B.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Llama-3-8B-Instruct-Gradient-1048k.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Llama-3.1-8B-Instruct.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Qwen2.5-72B-Instruct.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Qwen2.5-7B-Instruct-1M.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Qwen2.5-7B-Instruct.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Qwen3-30B-A3B-Thinking-2507.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Qwen3-4B-Thinking-2507.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Qwen3-8B-Instruct.json` | Dependency, configuration, or usage evidence. |
| `official-code/config/Qwen3-8B.json` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/cache_hub/collision_fused/collision_test.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cache_hub/cache.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cache_hub/polar_cache.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cache_hub/polar_cache_atten_value_indices_adaptive_k.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cache_hub/polar_cache_adaptivek_varlen.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cache_hub/gather/cpp_gather.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cache_hub/collision_fused/collison_interface.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cache_hub/collision/collision.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/cache_hub/gather_trans/trans_h2d.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
