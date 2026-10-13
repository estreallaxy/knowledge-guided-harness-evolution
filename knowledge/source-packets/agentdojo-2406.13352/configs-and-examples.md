# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `pyproject.toml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `.devcontainer/Dockerfile` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `src/agentdojo/agent_pipeline/__init__.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `src/agentdojo/agent_pipeline/agent_pipeline.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `src/agentdojo/agent_pipeline/base_pipeline_element.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `src/agentdojo/agent_pipeline/basic_elements.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `src/agentdojo/agent_pipeline/errors.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `src/agentdojo/agent_pipeline/ground_truth_pipeline.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `src/agentdojo/agent_pipeline/pi_detector.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `src/agentdojo/agent_pipeline/planner.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
