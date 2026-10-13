# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/environment_cleanup.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/environment_setup.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/requirements.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/setup.sh` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/environment_editors/base_environment_editor.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/environment_editors/gitlab_editor.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/environment_editors/reddit_editor.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/environment_editors/__init__.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/scripts/step1_setup_prompt_injections.sh` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/configs/croissant/generate_croissant_metadata.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `webarena_prompt_injections/configs/system_prompts/claude_35_agent.json` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `webarena_prompt_injections/constants.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `webarena_prompt_injections/environment_cleanup.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `webarena_prompt_injections/environment_setup.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `webarena_prompt_injections/evaluator_step_by_step.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `webarena_prompt_injections/evaluator_step_by_step_utils.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `webarena_prompt_injections/prompt_injector.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `webarena_prompt_injections/requirements.txt` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `webarena_prompt_injections/run.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
