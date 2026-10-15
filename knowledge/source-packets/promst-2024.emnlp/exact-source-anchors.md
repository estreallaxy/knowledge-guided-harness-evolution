# Exact source anchors

## Selected mechanism

Convert multi-step execution failures into structured feedback rules and let an LLM revise the task prompt; retain only the rule-conditioned revision path.

## Paper anchors

- p. 1: framework PRompt Optimization in Multi-Step LLM-driven agents solving multi-step tasks and
- p. 2: framework and investigate the underlying reasons to modify an initial prompt, driven either by rein-
- p. 4: evaluation, and multi-step tasks can be much more across all tasks (e.g. syntactic errors), while others
- p. 4: Algorithm 2 in Appendix B shows the process ate over possible versions of feedback templates
- p. 5: method but without the rules of human feedback. 4 (gpt-4-turbo-preview) (Achiam et al., 2023) as
- p. 6: 4.4 Results and Analysis score vs the actual score for various prompts; blue
- p. 7: results show that both the training and testing paths
- p. 8: Ablation on SumLLM Component Since marizing detailed careful points into varying token
- p. 8: framework, we compare PROMST with/without mance. The results indicate that task scores consis-
- p. 8: Ablation on Human Feedback We compare Comparison and Combination with Reflexion
- p. 8: results show that variability over the wording of the agent tasks: PROMST. To handle the issues of task
- p. 9: 6 Limitations

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/tests/test_searchandrescue.py`
- `Logistics/env_data_Logistics/pddlgym/tests/test_searchandrescue.py`
- `BlocksWorld/env7-blocksworld-list-score.py`
- `BlocksWorld/prompt_env7.py`
- `BoxLift/env3-boxlift-list-score.py`
- `BoxLift/prompt_env3.py`
- `BoxNet1/env1-boxnet1-list-score.py`
- `BoxNet1/prompt_env1.py`
- `BoxNet2/env2-boxnet2-list-score.py`
- `BoxNet2/prompt_env2.py`
- `GridWorld1/env5-gridworld1-list-score.py`
- `GridWorld1/prompt_env5.py`
- `GridWorld2/env6-gridworld2-list-score.py`
- `GridWorld2/prompt_env6.py`
- `Logistics/env8-logistics-list-score.py`
- `Logistics/prompt_env8.py`
- `WareHouse/env4-warehouse-list-score.py`
- `WareHouse/prompt_env4.py`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/tests/test_inference.py`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/tests/test_parser.py`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/tests/test_pddlenv.py`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/tests/test_spaces.py`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/tests/test_system.py`
- `Logistics/env_data_Logistics/pddlgym/tests/test_inference.py`
- `Logistics/env_data_Logistics/pddlgym/tests/test_parser.py`
- `Logistics/env_data_Logistics/pddlgym/tests/test_pddlenv.py`
- `Logistics/env_data_Logistics/pddlgym/tests/test_spaces.py`
- `Logistics/env_data_Logistics/pddlgym/tests/test_system.py`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/downward_translate/tests/test_normalization.py`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/downward_translate/tests/test_scripts.py`
- `Logistics/env_data_Logistics/pddlgym/downward_translate/tests/test_normalization.py`
- `Logistics/env_data_Logistics/pddlgym/downward_translate/tests/test_scripts.py`
- `BlocksWorld/env_data_BlocksWorld/pddlgym/demo_planning.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The rule/feedback-to-revision loop is separable and training-free. The learned prompt-performance predictor is explicitly out of scope; experiments and code allow the revision mechanism to be tested without adopting that trained component.

## Symbol-level code anchors

- `BlocksWorld/env_data_BlocksWorld/pddlgym/tests/test_searchandrescue.py:4` — `test_searchandrescue`
- `Logistics/env_data_Logistics/pddlgym/tests/test_searchandrescue.py:4` — `test_searchandrescue`
- `BlocksWorld/env7-blocksworld-list-score.py:9` — `read_file_content`
- `BlocksWorld/prompt_env7.py:8` — `input_prompt_1_func_total`
- `BoxLift/env3-boxlift-list-score.py:9` — `read_file_content`
- `BoxLift/prompt_env3.py:8` — `input_prompt_1_func_total`
- `BoxNet1/env1-boxnet1-list-score.py:9` — `read_file_content`
- `BoxNet1/prompt_env1.py:8` — `input_prompt_1_func_total`
- `BoxNet2/env2-boxnet2-list-score.py:8` — `read_file_content`
- `BoxNet2/prompt_env2.py:8` — `input_prompt_1_func_total`
- `GridWorld1/env5-gridworld1-list-score.py:8` — `read_file_content`
- `GridWorld1/prompt_env5.py:8` — `input_prompt_1_func_total`
