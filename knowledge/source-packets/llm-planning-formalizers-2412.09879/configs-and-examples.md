# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/README.md` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/Barman-100/heavily_templated_dd.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/Barman-100/heavily_templated_pd.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/Logistics-100/heavily_templated_dd.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/Logistics-100/heavily_templated_pd.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/Logistics-100/moderately_templated_dd.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/Logistics-100/moderately_templated_pd.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/Logistics-100/natural_dd.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |
| `examples/Logistics-100/natural_pd.txt` | 核心方法所需的依赖、参数、配置或最小示例。 |

## Method 接入入口

| 文件 | 使用方式 |
| --- | --- |
| `source/llm-as-formalizer.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `source/llm-as-planner.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `source/run_solver.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |
| `source/run_val.py` | 方法实现或直接执行入口；按官方 README 补齐模型、数据与外部服务。 |

## 本地保存范围

`official-code/` 仅保存论文方法的核心实现、直接依赖接口、最小配置/示例/测试和许可证。大型外部数据、通用框架副本、缓存与论文实验输出未纳入。
