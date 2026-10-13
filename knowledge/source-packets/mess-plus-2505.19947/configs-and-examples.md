# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `pyproject.toml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `requirements.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `classifier/sweep_config.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `config/qwen2/piqa.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `config/qwen2/sciq.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `config/qwen2/social_iqa.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `config/qwen2/winogrande.yaml` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `main.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `utils/mess_plus/__init__.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `utils/mess_plus/bernoulli_sampler.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `simulator.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `algorithm/exploitation.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `algorithm/exploration.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `algorithm/update_q.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `algorithm/__init__.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
