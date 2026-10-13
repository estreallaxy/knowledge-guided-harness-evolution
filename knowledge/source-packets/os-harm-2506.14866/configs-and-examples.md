# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `.mise.toml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `pyproject.toml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `requirements.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `setup.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `mm_agents/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `desktop_env/controllers/setup.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `desktop_env/evaluators/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `desktop_env/providers/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `desktop_env/server/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `desktop_env/server/requirements.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `evaluation_examples/examples/vs_code/___check_self_eval_prompt.json` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `mm_agents/__init__.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `mm_agents/agent.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `mm_agents/aguvis_agent.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `mm_agents/uitars_agent.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `judge/methods/aer.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `judge/methods/all_step_aer.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `judge/methods/plain_judge.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `mm_agents/accessibility_tree_wrap/__init__.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
