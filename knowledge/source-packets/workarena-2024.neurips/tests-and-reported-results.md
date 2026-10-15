# Tests and reported results

## Official verification entry points

- `tests/test_random_config_generation.py`
- `tests/test_task_from_config.py`
- `src/browsergym/workarena/data_files/task_configs/dashboard_retrieval_minmax_task.json`
- `src/browsergym/workarena/data_files/task_configs/dashboard_retrieval_value_task.json`
- `src/browsergym/workarena/data_files/task_configs/report_retrieval_minmax_task.json`
- `src/browsergym/workarena/data_files/task_configs/report_retrieval_value_task.json`
- `src/workarena_test.py`
- `tests/conftest.py`
- `tests/test_api.py`
- `tests/test_compositional.py`
- `tests/test_compositional_binding.py`
- `tests/test_compositional_utils.py`
- `tests/test_filter_list_task.py`
- `tests/test_instance_preconditions.py`
- `tests/test_snow_instance.py`
- `tests/test_task_general.py`
- `tests/test_task_setup.py`
- `tests/test_utils.py`
- `tests/test_validate.py`
- `tests/utils.py`
- `make_human_eval_curriculum.py`
- `src/browsergym/workarena/human_eval/tool.py`
- `scripts/make_human_eval_curriculum.py`
- `src/browsergym/workarena/human_eval/console.js`

## Published result anchors

- p. 5: Table 1: Comparing existing web-agent evaluation benchmarks with WorkArena++.
- p. 8: Table 2: Success rate±Standard error (SR ±SE) of all agents on MiniWoB, WorkArena, and WebArena, with numbers
- p. 56: Table 3: Ablation study for Llama3 on WorkArena-L1. Success rate±Standard error (SR ±SE).

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | 2024, NeurIPS Datasets and Benchmarks |
| Official open-source implementation | https://github.com/ServiceNow/WorkArena at `e885130962f61fb64ac305497996a46cfc7d18f0` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
