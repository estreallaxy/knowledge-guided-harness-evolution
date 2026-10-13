# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `codes/deepspeed_configurations.json` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `demo/500xCompressor_demo.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `demo/ICAE_demo.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `demo/L3ICAE.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `demo/L3LoraL3.py` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `env/conda_requirements.yml` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `env/pip_requirements.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `demo/500xCompressor_demo.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `codes/finetuning/finetune_500xCompressor.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `codes/prediction/predict_qa_500xCompressor.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `codes/prediction/predict_regenerate_500xCompressor.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `codes/pretraining/train_500xCompressor.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `demo/ICAE_demo.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `demo/L3ICAE.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `demo/L3LoraL3.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
