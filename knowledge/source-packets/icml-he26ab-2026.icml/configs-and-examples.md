# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/p2p_comm/python_api/examples/bm25_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/p2p_comm/python_api/examples/gpu_to_fpga_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/p2p_comm/python_api/examples/p2p_demo.py` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/backend/modeling/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/backend/modeling/fpga_config/fpga_resource.json` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/backend/modeling/fpga_config/u55c.json` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/backend/modeling/pcie_config/p2p_host_jump.json` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/backend/profiling/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/dev/passes/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/dev/passes/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/dev/profile_test/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/dev/steps/example_kernel/bm25_fpga_retrieval.cpp` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/dev/steps/example_kernel/rag_apply_memory.cpp` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/dev/steps/example_kernel/threshold_retrieval.cpp` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/dev/steps/example_kernel/topk_retrieval.cpp` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/frontend/dev/unittest/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/rag_test/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/toolchain/rag_test/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/toolchain/rag_test/run_bm25_loader.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
