# Tests and reported results

## Official verification entry points

- `BlocksWorld/env_data_BlocksWorld/pddlgym/tests/test_searchandrescue.py`
- `Logistics/env_data_Logistics/pddlgym/tests/test_searchandrescue.py`
- `BlocksWorld/env7-blocksworld-list-score.py`
- `BoxLift/env3-boxlift-list-score.py`
- `BoxNet1/env1-boxnet1-list-score.py`
- `BoxNet2/env2-boxnet2-list-score.py`
- `GridWorld1/env5-gridworld1-list-score.py`
- `GridWorld2/env6-gridworld2-list-score.py`
- `Logistics/env8-logistics-list-score.py`
- `WareHouse/env4-warehouse-list-score.py`
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

## Published result anchors

- p. 7: Table 1: Scores for initial (human) and optimized prompts on various multi-step tasks for different methods.
- p. 7: Table 2: Scores for initial (human) and optimized prompts on various multi-step tasks for different
- p. 8: Table 3: Evaluation of different LLMs on a subset of the mutli-step tasks. The same LLM was used for
- p. 8: Table 4: Ablation studies on SumLLM.
- p. 9: Table 5: Ablation studies on the templates used for human feedback.
- p. 13: Table 6: Types of human feedback for each task
- p. 18: Table 7: Scores for initial and optimized prompts using different types of LLMs as TaskLLM. The opti-
- p. 18: Table 8: Scores for initial and optimized prompts using different types of LLMs as TaskLLM. The
- p. 19: Table 9: Corresponding values of task progress rates (score format used in our study) and task completion
- p. 26: Table 10: Comparison and combination with dynamic approach Reflexion.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | EMNLP 2024 |
| Official open-source implementation | https://github.com/yongchao98/PROMST at `64a0785e7520cb775980596d315394c05cd92d9c` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
