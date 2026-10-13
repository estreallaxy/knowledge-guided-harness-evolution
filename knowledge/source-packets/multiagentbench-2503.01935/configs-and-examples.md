# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `.pre-commit-config.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `pyproject.toml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `.github/workflows/ruff.yml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `marble/configs/prompt_config.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `marble/utils/milestone_prompt.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `marble/agent/werewolf_prompts/arena_prompts.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `marble/agent/werewolf_prompts/badge_flow.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `marble/agent/werewolf_prompts/decide_speech_sequence.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `marble/agent/werewolf_prompts/eval_communication.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `marble/agent/werewolf_prompts/eval_competiveness.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `marble/agent/werewolf_prompts/eval_prompts.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `marble/main.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `marble/engine/engine_planner.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `marble/graph/agent_graph.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `marble/evaluator/env_evaluation_prompts.json` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `marble/evaluator/evaluator_prompts.json` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `multiagentbench/jsonl2yaml.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `multiagentbench/runjsonl2yaml.sh` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `tests/test_model_prompting.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
