# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `data_prepare/process_example.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `SENSE/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `data_prepare/1_goal/config.json` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `data_prepare/2_private_info/config.json` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `SENSE/configs/judge_config.json` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `SENSE/configs/prompt_template.json` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `SENSE/commands/example/gpt4o.sh` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `SENSE/commands/example/heter_gpt4o_gpt35.sh` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `SENSE/commands/example/llama3_8b.sh` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `SENSE/initialization.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `SENSE/metric.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `SENSE/run_eval.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `SENSE/simulation.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `SENSE/commands/example/gpt4o.sh` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `SENSE/commands/example/heter_gpt4o_gpt35.sh` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `SENSE/commands/example/llama3_8b.sh` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `SENSE/configs/judge_config.json` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
