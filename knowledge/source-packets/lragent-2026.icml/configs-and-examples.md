# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/src/langchain/prompts/example_selector/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/langchain/prompts/example_selector/base.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/langchain/prompts/example_selector/length_based.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/langchain/prompts/example_selector/ngram_overlap.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/peft/method_comparison/text_generation_benchmark/configs/prompts.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/transformers/examples/flax/_tests_requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/transformers/examples/legacy/seq2seq/old_test_fsmt_bleu_score.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/transformers/examples/legacy/seq2seq/run_eval_search.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/transformers/examples/legacy/seq2seq/test_data/fsmt/build-eval-data.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/transformers/examples/pytorch/_tests_requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/transformers/examples/research_projects/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/transformers/examples/tensorflow/_tests_requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/Self_Plan/Group_Planning/benchmark_run/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/transformers/examples/legacy/seq2seq/run_eval_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/transformers/src/transformers/agents/evaluate_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
