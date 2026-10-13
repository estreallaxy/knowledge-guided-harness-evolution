# Configs and examples

##Environment and configuration entry

|document|use|
| --- | --- |
| `src/archon/benchmarks/itas_algorithms/search_configs/example_search_config.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-70Bx10_SOTA_1_samples_then_unit_test_generation_then_unit_test_evaluation_then_fuse.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-70Bx10_SOTA_1_samples_then_unit_test_generation_then_unit_test_evaluation_then_pass_top_cand.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-code_70Bx6_1_samples_then_unit_test_generation_with_gpt4_turbo_then_unit_test_evaluation_with_gpt4_turbo_then_pass_top_cand.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_1000_then_unit_test_generation_10_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_1000_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_100_temp_0.85_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_100_temp_1.0_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_100_temp_1.25_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_100_temp_1.5_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_100_then_unit_test_generation_10_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_100_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_10_then_unit_test_generation_10_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_10_then_unit_test_generation_20_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_10_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|
| `src/archon/configs/archon-gpt-4o-sample_1_then_unit_test_generation_10_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` |Dependencies, parameters, configuration or running example entry|

## Execution entry

|document|Usage|
| --- | --- |
| `src/archon/benchmarks/code_contests/eval_code_contests.py` |Official code entry candidate; complete model, data and external services according to README before running.|
| `src/archon/benchmarks/mt_bench/eval_mt_bench.py` |Official code entry candidate; complete model, data and external services according to README before running.|

## Local saving range

`official-code/`saves the core source code, configuration, examples and test entries of the official repository under a fixed revision. The complete data set, model weights, cache and paper experimental output must be obtained separately from the official README.
