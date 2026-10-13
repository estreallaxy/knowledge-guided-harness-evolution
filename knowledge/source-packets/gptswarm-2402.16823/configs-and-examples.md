# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `swarm/environment/domain/gaia/evaluation/README.md` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/domain/gaia/evaluation/requirements.txt` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/prompt/humaneval_prompt_set.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/prompt/human_eval_fewshot.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/agents/gaia/tool_io.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/agents/gaia/tool_tot.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/agents/humaneval/code_io.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/agents/humaneval/code_react.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/domain/crosswords/evaluator.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/operations/humaneval/unitest_generation.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/tools/coding/README.md` | 依赖、参数、配置或运行示例入口 |
| `test/swarm/environment/agents/test_cot.py` | 依赖、参数、配置或运行示例入口 |
| `test/swarm/environment/agents/test_io.py` | 依赖、参数、配置或运行示例入口 |
| `test/swarm/environment/prompt/test_prompt_set_registry.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/domain/gaia/evaluation/app.py` | 依赖、参数、配置或运行示例入口 |
| `swarm/environment/domain/gaia/evaluation/content.py` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `swarm/environment/domain/gaia/evaluation/app.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/run_humaneval.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/run_crosswords.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/run_gaia.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/run_mmlu.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/crosswords/train.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
