# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `requirements.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/Dockerfile` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/requirements.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/aios/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/aios/context/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/aios/llm_core/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/aios/memory/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/aios/scheduler/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/aios/storage/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `ASB_DRIFT/aios/utils/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `DRIFTLLM.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `DRIFTTaskSuite.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `DRIFTToolsExecutionLoop.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `ASB_DRIFT/main_attacker.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `ASB_DRIFT/requirements.txt` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `ASB_DRIFT/memory_defense/llm_dection.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `ASB_DRIFT/memory_defense/llm_utils.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `ASB_DRIFT/memory_defense/ppl_dection.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
