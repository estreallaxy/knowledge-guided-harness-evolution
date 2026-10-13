# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `rrutils/message_poller/src/setupTests.js` | 依赖、参数、配置或运行示例入口 |
| `monitoring/experiments_setup_notebook.py` | 依赖、参数、配置或运行示例入口 |
| `monitoring/problem_setup.py` | 依赖、参数、配置或运行示例入口 |
| `elk/func_correct/config.json` | 依赖、参数、配置或运行示例入口 |
| `rrutils/message_poller/README.md` | 依赖、参数、配置或运行示例入口 |
| `elk/func_correct/exec/config.json` | 依赖、参数、配置或运行示例入口 |
| `elk/func_correct/exec/Dockerfile` | 依赖、参数、配置或运行示例入口 |
| `elk/func_correct/exec/setup_lines.py` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `monitoring/run_code.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `rrutils/message_poller/src/App.js` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
