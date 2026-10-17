# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/GPQA/prompts/chain_of_thought_examples.json` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/IFEval/instruction_following_eval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/IFEval/instruction_following_eval/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/prompts/few_shot_examples/generation/func.json` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/LiveCodeBench/lcb_runner/prompts/few_shot_examples/generation/stdin.json` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_deepseek_chat.sh` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_deepseek_coder.sh` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gemini_flash.sh` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gemini_flash_8b.sh` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gemini_pro.sh` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gpt_4.sh` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gpt_4o.sh` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_llama_2_7b.sh` | Dependency, configuration, or usage evidence. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_mixtral_7b.sh` | Dependency, configuration, or usage evidence. |
| `official-code/global_utils/runtime_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/smcs_config.example.json` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/benchmarks/HumanEval/run_api.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/HumanEval/run_exp.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/IFEval/run_exp.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/evaluate_from_api.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/evaluate_from_local.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_deepseek_chat.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_deepseek_coder.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gemini_flash.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gemini_flash_8b.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gemini_pro.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gpt_4.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_gpt_4o.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_llama_2_7b.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/benchmarks/MMLU-PRO/scripts/examples/eval_mixtral_7b.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_exp.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
