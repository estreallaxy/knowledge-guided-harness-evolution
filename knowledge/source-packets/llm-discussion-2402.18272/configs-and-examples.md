# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `examples/evaluation-plan.json` | 依赖、参数、配置或运行示例入口 |
| `examples/openrouter.json` | 依赖、参数、配置或运行示例入口 |
| `tests/test_config.py` | 依赖、参数、配置或运行示例入口 |
| `src/llm_discussion/config.py` | 依赖、参数、配置或运行示例入口 |
| `pyproject.toml` | 依赖、参数、配置或运行示例入口 |
| `README.md` | 依赖、参数、配置或运行示例入口 |
| `data/README.md` | 依赖、参数、配置或运行示例入口 |
| `examples/math-suite.json` | 依赖、参数、配置或运行示例入口 |
| `examples/mixed-models.json` | 依赖、参数、配置或运行示例入口 |
| `examples/vision-suite.json` | 依赖、参数、配置或运行示例入口 |
| `.github/workflows/tests.yml` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `scripts/run_evaluation.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `src/llm_discussion/cli.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
