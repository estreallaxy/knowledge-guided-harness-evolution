# Configs and examples

## 环境与配置入口

| 文件 | 用途 |
| --- | --- |
| `scripts/run_suite_on_docker.py` | 依赖、参数、配置或运行示例入口 |
| `docker_setup/entrypoint.sh` | 依赖、参数、配置或运行示例入口 |
| `docker_setup/start_emu.sh` | 依赖、参数、配置或运行示例入口 |
| `docker_setup/start_emu_headless.sh` | 依赖、参数、配置或运行示例入口 |
| `android_world/agents/README.md` | 依赖、参数、配置或运行示例入口 |
| `android_world/env/setup_device/setup_test.py` | 依赖、参数、配置或运行示例入口 |
| `Dockerfile` | 依赖、参数、配置或运行示例入口 |
| `pyproject.toml` | 依赖、参数、配置或运行示例入口 |
| `README.md` | 依赖、参数、配置或运行示例入口 |
| `requirements.txt` | 依赖、参数、配置或运行示例入口 |
| `setup.py` | 依赖、参数、配置或运行示例入口 |
| `.github/workflows/pytest.yml` | 依赖、参数、配置或运行示例入口 |
| `android_world/env/setup_device/apps.py` | 依赖、参数、配置或运行示例入口 |
| `android_world/env/setup_device/setup.py` | 依赖、参数、配置或运行示例入口 |
| `android_world/env/setup_device/__init__.py` | 依赖、参数、配置或运行示例入口 |

## 执行入口

| 文件 | 使用方式 |
| --- | --- |
| `scripts/run_suite_on_docker.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |
| `run.py` | 官方代码入口候选；运行前按 README 补齐模型、数据和外部服务。 |

## 本地保存范围

`official-code/` 保存官方仓库在固定 revision 下的核心源代码、配置、示例和测试入口。完整数据集、模型权重、缓存和论文实验输出需按官方 README 另行取得。
