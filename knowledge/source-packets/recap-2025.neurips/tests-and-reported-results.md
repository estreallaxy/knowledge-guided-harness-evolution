# Tests and reported results

## Official verification entry points

- `robotouille-baselines/pddlgym/downward_translate/regression-tests/README`
- `robotouille-recap/pddlgym/downward_translate/regression-tests/README`
- `swebench-recap/sweagent/run/rich_test.py`
- `swebench-recap/sweagent/run/hooks/swe_bench_evaluate.py`
- `robotouille-baselines/environments/env_generator/examples/test_arena.json`
- `robotouille-recap/environments/env_generator/examples/test_arena.json`
- `robotouille-baselines/backend/tests/action_test.py`
- `robotouille-baselines/pddlgym/tests/test_searchandrescue.py`

## Published result anchors

- p. 7: Table 1: Pass@1 task success rates (%) across methods.
- p. 9: Table 2: Success rates (%) between ReAct and ReCAP across models, Robotouille tasks #2, 4, and 6.
- p. 9: Table 3: Success rates (%) between different ReCAP structural variants, Robotouille task # 6.
- p. 22: Table 4: Performance comparison between ReCAP and baselines on Robotouille synchronous tasks
- p. 22: Table 5: Performance comparison between ReCAP and baselines on Robotouille asynchronous tasks

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2025 |
| Official open-source implementation | https://github.com/ReCAP-Stanford/ReCAP at `2fb112ffad685c7c6f7de86d5487ecca6f566fcc` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
