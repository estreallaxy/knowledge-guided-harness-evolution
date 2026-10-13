# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `pyproject.toml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `.github/workflows/build.yml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `.github/workflows/ci.yml` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `toolmaker/agent/__init__.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `toolmaker/agent/agent.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `toolmaker/agent/state.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `scripts/toolmaker_function_runner.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `toolmaker/cli.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `toolmaker/definition.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `toolmaker/run.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `toolmaker/__init__.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
