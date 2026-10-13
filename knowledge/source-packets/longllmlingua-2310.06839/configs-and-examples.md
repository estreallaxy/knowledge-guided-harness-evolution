# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `examples/RAGLlamaIndex.ipynb` | 依赖、参数、配置或运行示例入口 |
| `examples/Retrieval.ipynb` | 依赖、参数、配置或运行示例入口 |
| `.pre-commit-config.yaml` | 依赖、参数、配置或运行示例入口 |
| `pyproject.toml` | 依赖、参数、配置或运行示例入口 |
| `README.md` | 依赖、参数、配置或运行示例入口 |
| `setup.cfg` | 依赖、参数、配置或运行示例入口 |
| `setup.py` | 依赖、参数、配置或运行示例入口 |
| `examples/Code.ipynb` | 依赖、参数、配置或运行示例入口 |
| `examples/CoT.ipynb` | 依赖、参数、配置或运行示例入口 |
| `examples/LLMLingua2.ipynb` | 依赖、参数、配置或运行示例入口 |
| `examples/OnlineMeeting.ipynb` | 依赖、参数、配置或运行示例入口 |
| `examples/RAG.ipynb` | 依赖、参数、配置或运行示例入口 |
| `.github/ISSUE_TEMPLATE/config.yml` | 依赖、参数、配置或运行示例入口 |
| `.github/workflows/unittest.yml` | 依赖、参数、配置或运行示例入口 |
| `experiments/llmlingua2/README.md` | 依赖、参数、配置或运行示例入口 |
| `experiments/securitylingua/env_setup.sh` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `experiments/securitylingua/run.sh` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/securitylingua/train_roberta.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/llmlingua2/evaluation/eval_bbh.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/llmlingua2/evaluation/eval_gsm8k.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/llmlingua2/evaluation/eval_longbench.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/llmlingua2/evaluation/eval_meetingbank_qa.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/llmlingua2/evaluation/eval_meetingbank_summary.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/llmlingua2/evaluation/eval_zero_scrolls.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/llmlingua2/model_training/train.sh` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `experiments/llmlingua2/model_training/train_roberta.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
