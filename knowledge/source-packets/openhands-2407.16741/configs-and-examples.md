# Configs and examples

## 官方配置

| 设置 | 配置目录 | 主要内容 |
| --- | --- | --- |
| 沙箱与运行时 | `official-code/openhands/core/config/sandbox_config.py` | base 镜像默认 `nikolaik/python-nodejs:python3.12-nodejs22`（:49-51）；`runtime_container_image` 默认 None（:52）；`:24/33` 注释提到 `runtime_extra_deps` 用于评测、`browsergym_eval_env` 指向 `evaluation/miniwob`、`evaluation/webarena`。 |
| LLM 接入 | `official-code/openhands/core/config/llm_config.py` | 默认 `model='claude-3-7-sonnet-20250219'`、`api_key=None`（:49-50），运行时填入。 |
| 评测相关参数 | `official-code/openhands/core/config/utils.py:494-499` | `--eval` 相关参数；默认输出目录 `evaluation/evaluation_outputs/outputs`。 |

配置只能和对应论文版本、代码 revision、任务数据与模型环境一起解释。论文中的运行结果不能由单个配置独立复现。

## 官方流程入口

官方 README（本包内为 `official-code/README.upstream.md`）给出的容器运行方式（:54-66）：

```bash
docker pull docker.all-hands.dev/all-hands-ai/runtime:0.33-nikolaik

docker run -it --rm --pull=always \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.33-nikolaik \
  -e LOG_ALL_EVENTS=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands-state:/.openhands-state \
  -p 3000:3000 \
  --name openhands-app \
  docker.all-hands.dev/all-hands-ai/openhands:0.33
```

运行前提：

- 宿主机 Docker 且挂载 `docker.sock`（README:60）；镜像构建器 `official-code/openhands/runtime/builder/docker.py:16`、Docker runtime `official-code/openhands/runtime/impl/docker/docker_runtime.py:57`。
- 模型 API key：首次启动选择 LLM provider 并填写（README:70-72，推荐 `anthropic/claude-3-5-sonnet-20241022`）。
- headless 入口：`official-code/openhands/core/main.py:48`（run_controller）、`:56`（headless_mode=True，默认）。
- 本快照不含 `pyproject.toml`/`requirements`、`storage/`、`llm/`、`server/` 等模块（`official-code/openhands/events/stream.py:15` 的 `from openhands.storage import FileStore` 指向快照外），完整运行需上游仓库。

## 本地保存范围

`official-code/` 保存 `openhands/` 的 agenthub（codeact_agent、browsing_agent、dummy_agent、readonly_agent、visualbrowsing_agent 及其 prompts/tools）、controller、core/config、events、memory、runtime 与 `README.upstream.md`、`LICENSE`。

评测侧说明：快照中**不存在** `evaluation/` 目录（顶层目录仅 openhands/、README.upstream.md、LICENSE）；论文评测所用脚本（含 SWE-bench、WebArena、MiniWoB++、GAIA 集成）需从 OpenHands 主仓库另行获取。
