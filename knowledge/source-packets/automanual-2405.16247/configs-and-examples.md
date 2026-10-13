# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `alfworld/configs/eval_config.yaml` | 依赖、参数、配置或运行示例入口 |
| `alfworld/docker/docker_run.py` | 依赖、参数、配置或运行示例入口 |
| `alfworld/scripts/README.md` | 依赖、参数、配置或运行示例入口 |
| `automanual_alfworld/prompts/autobuild_examples.py` | 依赖、参数、配置或运行示例入口 |
| `automanual_alfworld/prompts/autobuild_simple_examples.py` | 依赖、参数、配置或运行示例入口 |
| `automanual_alfworld/prompts/base_examples.py` | 依赖、参数、配置或运行示例入口 |
| `automanual_miniwob/prompts/autobuild_examples.py` | 依赖、参数、配置或运行示例入口 |
| `automanual_miniwob/prompts/autobuild_simple_examples.py` | 依赖、参数、配置或运行示例入口 |
| `automanual_miniwob/prompts/base_examples.py` | 依赖、参数、配置或运行示例入口 |
| `automanual_webarena/config_files/test.raw.json` | 依赖、参数、配置或运行示例入口 |
| `alfworld/alfworld/agents/README.md` | 依赖、参数、配置或运行示例入口 |
| `automanual_webarena/config_files/examples/1.json` | 依赖、参数、配置或运行示例入口 |
| `automanual_webarena/config_files/examples/2.json` | 依赖、参数、配置或运行示例入口 |
| `automanual_webarena/config_files/examples/3.json` | 依赖、参数、配置或运行示例入口 |
| `automanual_webarena/config_files/examples/4.json` | 依赖、参数、配置或运行示例入口 |
| `automanual_webarena/prompts/examples/gitlab_examples.py` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `alfworld/scripts/run_eval.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `automanual_alfworld/main_test.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `automanual_miniwob/main_test.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `automanual_webarena/main_test.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `alfworld/scripts/train_dagger.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `alfworld/scripts/train_dqn.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `alfworld/scripts/train_mrcnn.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `alfworld/scripts/train_seq2seq.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `alfworld/scripts/train_vision_dagger.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `alfworld/alfworld/agents/detector/train.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `automanual_miniwob/computergym/miniwob/miniwob_interface/html/flight/Alaska/scripts/main.js` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `automanual_miniwob/computergym/miniwob/miniwob_interface/html/flight/Alaska-auto/scripts/main.js` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
