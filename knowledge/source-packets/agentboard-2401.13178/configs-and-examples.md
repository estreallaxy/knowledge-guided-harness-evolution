# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `agentboard/environment/pddl_env/pddlgym/downward_translate/regression-tests/README` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/pddl_env/pddlgym/downward_translate/tests/test_scripts.py` | 依赖、参数、配置或运行示例入口 |
| `eval_configs/main_results_all_tasks.yaml` | 依赖、参数、配置或运行示例入口 |
| `eval_configs/.ipynb_checkpoints/main_results_all_tasks-checkpoint.yaml` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/alfworld/base_config.yaml` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/browser_env/env_config.py` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/browser_env/evaluation_function.py` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/WebShop/LICENSE.md` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/WebShop/README.md` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/WebShop/run_dev.sh` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/WebShop/run_web_agent_site_env.sh` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/WebShop/run_web_agent_text_env.sh` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/WebShop/setup.sh` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/pddl_env/pddlgym/demo.py` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/pddl_env/pddlgym/demo_planning.py` | 依赖、参数、配置或运行示例入口 |
| `agentboard/environment/WebShop/search_engine/run_indexing.sh` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `agentboard/eval_main.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `agentboard/environment/WebShop/run_dev.sh` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `agentboard/environment/WebShop/run_web_agent_site_env.sh` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `agentboard/environment/WebShop/run_web_agent_text_env.sh` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `agentboard/environment/pddl_env/pddlgym/demo.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `agentboard/environment/pddl_env/pddlgym/demo_planning.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `agentboard/environment/WebShop/search_engine/run_indexing.sh` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `agentboard/environment/WebShop/web_agent_site/app.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
