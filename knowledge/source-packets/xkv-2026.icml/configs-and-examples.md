# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/example.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/grouped_layers.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/efficiency/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/efficiency/build_kernel.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/efficiency/run_benchmarks.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV/eval_ablation_window.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV/eval_longbench_llama.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV/eval_quant.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV/eval_ruler_llama.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV/eval_ruler_qwen.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV_SR/eval_longbench_llama.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV_SR/eval_longbench_qwen.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV_SR/eval_ruler_llama.sh` | Dependency, configuration, or usage evidence. |
| `official-code/examples/xKV_SR/eval_ruler_qwen.sh` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/tests/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/xKV/configurations.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/evaluate/eval_acc.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/efficiency/run_benchmarks.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV/eval_ablation_window.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV/eval_longbench_llama.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV/eval_quant.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV/eval_ruler_llama.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV/eval_ruler_qwen.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV_SR/eval_longbench_llama.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV_SR/eval_longbench_qwen.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV_SR/eval_ruler_llama.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/examples/xKV_SR/eval_ruler_qwen.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
