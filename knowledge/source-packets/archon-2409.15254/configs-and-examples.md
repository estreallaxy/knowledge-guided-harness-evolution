# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `src/archon/benchmarks/itas_algorithms/search_configs/example_search_config.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-70Bx10_SOTA_1_samples_then_unit_test_generation_then_unit_test_evaluation_then_fuse.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-70Bx10_SOTA_1_samples_then_unit_test_generation_then_unit_test_evaluation_then_pass_top_cand.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-code_70Bx6_1_samples_then_unit_test_generation_with_gpt4_turbo_then_unit_test_evaluation_with_gpt4_turbo_then_pass_top_cand.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_1000_then_unit_test_generation_10_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_1000_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_100_temp_0.85_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_100_temp_1.0_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_100_temp_1.25_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_100_temp_1.5_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_100_then_unit_test_generation_10_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_100_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_10_then_unit_test_generation_10_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_10_then_unit_test_generation_20_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_10_then_unit_test_generation_5_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |
| `src/archon/configs/archon-gpt-4o-sample_1_then_unit_test_generation_10_with_gpt-4o_then_unit_test_evaluation_with_gpt-4o_first_pass.json` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `src/archon/benchmarks/code_contests/eval_code_contests.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `src/archon/benchmarks/mt_bench/eval_mt_bench.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
