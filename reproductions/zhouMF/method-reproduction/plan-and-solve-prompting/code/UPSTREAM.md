# 上游代码快照说明

上游仓库：<https://github.com/AGI-Edgerunners/Plan-and-Solve-Prompting>

固定提交：`9d5a176f5b4de1011d426009ab6398dc76046e88`

```bash
git clone https://github.com/AGI-Edgerunners/Plan-and-Solve-Prompting.git
git -C Plan-and-Solve-Prompting checkout 9d5a176f5b4de1011d426009ab6398dc76046e88
```

## 本地整理（2026-10-12）

上游脚本使用过时 OpenAI completion API，因此只作来源保留，不参与运行：

| 路径 | 状态 |
| --- | --- |
| `code/upstream/` | 上游脚本原样快照（`prompt.py`、`main.py`、`utils.py`、`config.py`、`extracter.py`、`main_threads.py`、`prediction_runner.py` 与上游 README）。 |
| `code/plan_and_solve.py` | 本地实现：提示串逐字取自 `upstream/prompt.py`（`prompt_101` / `prompt_201` / `prompt_302`），与模型客户端解耦，可离线跑 `demo`。 |

已删除上游的占位凭据文件 `apikeys.json`（空 JSON 数组，仅作占位）；凭据改为只从环境变量读取。
