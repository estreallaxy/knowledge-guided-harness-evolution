# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `evaluation_examples/README.md` | 依赖、参数、配置或运行示例入口 |
| `evaluation_examples/test_all.json` | 依赖、参数、配置或运行示例入口 |
| `evaluation_examples/test_infeasible.json` | 依赖、参数、配置或运行示例入口 |
| `evaluation_examples/test_nogdrive.json` | 依赖、参数、配置或运行示例入口 |
| `evaluation_examples/test_small.json` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/maestro/tools/new_tools_config.json` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/os_symphony/tool/all_tool_config.yaml` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/README.md` | 依赖、参数、配置或运行示例入口 |
| `scripts/README.md` | 依赖、参数、配置或运行示例入口 |
| `desktop_env/evaluators/README.md` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/anthropic/README.md` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/aworldguiagent/README.md` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/kimi/README.md` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/m3/README.md` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/muse_spark/README.md` | 依赖、参数、配置或运行示例入口 |
| `mm_agents/pointer/config.py` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `mm_agents/surferH/run_benchmark_with_retries.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `scripts/python/run_multienv_aworldguiagent.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `scripts/python/run_multienv_mobileagent_v3.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `scripts/python/run_multienv_seedagent.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `mm_agents/anthropic/tools/run.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `mm_agents/anthropic/main.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `mm_agents/autoglm/main.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `mm_agents/autoglm_v/main.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `mm_agents/pointer/main.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `mm_agents/qwen/main.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `scripts/bash/run_dart_gui.sh` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `scripts/bash/run_gpt54.sh` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
