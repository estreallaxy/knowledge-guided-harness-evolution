# Exact source anchors

## Selected mechanism

Plan-ahead decomposition, execute-head/refine-tail recursion, parent-plan reinjection, bounded active context, and backtracking. Strict pass@1 experiments use frozen API models.

## Paper anchors

- p. 3: 2.1 Framework Overview
- p. 3: Algorithm 1 formalizes the overall procedure, starting from the entry point ReCAP(⟨D, Oinit ⟩) where
- p. 4: Algorithm 1 ReCAP
- p. 5: 3 Evaluation
- p. 5: framework’s ability to reliably solve real-world software issues [15].
- p. 7: 4 Results
- p. 9: Method GPT-4o Qwen2.5-32B Qwen2.5-72B LLaMA-4 (400B) DeepSeek-V3 (671B)
- p. 9: 4.4 Ablation Studies
- p. 14: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 16: results?
- p. 17: method aims to improve planning transparency and agent robustness in general-purpose
- p. 19: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `alfworld-recap/README.md`
- `alfworld-recap/pyproject.toml`
- `fever-recap/LICENSE.txt`
- `fever-recap/README.md`
- `fever-recap/requirements.txt`
- `robotouille-baselines/LICENSE`
- `robotouille-baselines/README.md`
- `robotouille-baselines/README_original.md`
- `robotouille-baselines/requirements.txt`
- `robotouille-baselines/setup.py`
- `robotouille-recap/LICENSE`
- `robotouille-recap/README.md`
- `robotouille-recap/requirements.txt`
- `swebench-recap/LICENSE`
- `swebench-recap/README.md`
- `swebench-recap/pyproject.toml`
- `alfworld-recap/MATRIX/requirements.txt`
- `robotouille-baselines/agents/README.md`
- `robotouille-recap/agents/README.md`
- `swebench-recap/config/README.md`
- `robotouille-baselines/agents/prompt_builder/README.md`
- `robotouille-baselines/environments/env_generator/README.md`
- `robotouille-baselines/renderer/configuration/README.md`
- `robotouille-recap/agents/prompt_builder/README.md`
- `robotouille-recap/environments/env_generator/README.md`
- `robotouille-recap/renderer/configuration/README.md`
- `swebench-recap/sweagent/inspector/README.md`
- `swebench-recap/tools/review_on_submit_m/README.md`
- `robotouille-baselines/agents/prompt_builder/gpt-cost-estimator/LICENSE`
- `robotouille-baselines/agents/prompt_builder/gpt-cost-estimator/README.md`
- `robotouille-baselines/agents/prompt_builder/gpt-cost-estimator/setup.py`
- `robotouille-baselines/pddlgym/downward_translate/regression-tests/README`
- `robotouille-recap/agents/prompt_builder/gpt-cost-estimator/LICENSE`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Plan-ahead decomposition, execute-head/refine-tail recursion, parent-plan reinjection, bounded active context, and backtracking. Strict pass@1 experiments use frozen API models.

## Symbol-level code anchors

- `robotouille-baselines/agents/prompt_builder/gpt-cost-estimator/README.md:24` — `query_openai`
- `robotouille-baselines/agents/in_context_examples/retrieve_example.py:6` — `retrieve_example`
- `robotouille-baselines/pddlgym/tests/test_searchandrescue.py:7` — `TestSearchAndRescue`
- `robotouille-recap/agents/in_context_examples/retrieve_example.py:6` — `retrieve_example`
- `swebench-recap/sweagent/run/rich_test.py:28` — `RunBatch`
- `swebench-recap/sweagent/run/hooks/swe_bench_evaluate.py:19` — `SweBenchEvaluate`
