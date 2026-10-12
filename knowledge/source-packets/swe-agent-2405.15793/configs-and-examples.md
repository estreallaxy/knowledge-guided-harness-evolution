# Configs and examples

## 官方配置

| 设置 | 配置目录 | 主要内容 |
| --- | --- | --- |
| 默认配置 | `official-code/config/default.yaml` | `WINDOW: 100`（:88）、`OVERLAP: 2`、`CURRENT_LINE/CURRENT_FILE`（:87-91）；`command_files` = `official-code/config/commands/` 下的 defaults.sh / search.sh / edit_linting.sh / _split_string.py / submit.sh（:92-97）；`parse_function: thought_action`（:111-112）；`history_processor: last_n_observations, n: 5`（:113-115）；`next_step_no_output_template`（:72-76）。 |
| 命令集 | `official-code/config/commands/` | 其内文件：defaults.sh（open/goto/scroll/create）、search.sh（search_dir/search_file/find_file）、edit_linting.sh（edit + flake8）、cursors_*.sh（游标式变体）、submit.sh、_split_string.py。 |
| 消融配置（现成可用） | `official-code/config/swe_agent_ablations/`（8 个 yaml） | `default|xml` × `window100|cursors_window100` × `full/last_5_history`；差异在 `WINDOW: 100 vs 200`、history_processor、command_files 是否换 cursors 版。另有 `config/default_xml.yaml`（XML 输出变体）。 |

配置只能和对应论文版本、代码 revision、任务数据与模型环境一起解释。论文中的运行结果不能由单个 YAML 独立复现（论文设置与快照默认也不同：论文最佳窗口 100/温度 0.0/Last-5，见 Table 5 p.25）。

## 官方流程入口

批量评测入口（命令形态存在，但见下方运行前提）：

```bash
python -m sweagent.run.run run-batch --config <yaml>
```

- 子命令 `run / run-batch / run-replay` 见 `official-code/sweagent/run/run.py:13-46`；CLI 由 `--config` 多次叠加（`official-code/sweagent/run/common.py:23-33`）。
- 产物落 `trajectories/<user>/<config>__<model>__<source>`（`official-code/sweagent/run/run_batch.py:33-43`）。
- 数据集实例由 `SWEBenchInstances` 从 HF `princeton-nlp/SWE-Bench[_Lite|_Verified]` 加载（`official-code/sweagent/run/batch_instances.py:203-243`）。

运行前提：

- Docker 镜像 `sweagent/swe-agent:latest`（`official-code/sweagent/environment/config/deployment.py:33-47`）与 SWE-bench 官方镜像 `swebench/sweb.eval.x86_64.*:v1`（`official-code/sweagent/run/batch_instances.py:129`）。
- `datasets` 包（加载 HF 数据集）；容器内自动 `pip install flake8`（`official-code/sweagent/tools/tools.py:78`）。
- 本快照不含 `pyproject.toml`/`requirements`、`frontend/`、`api/`、`evaluation`；也不含论文使用的 `trajectories/demonstrations/*.traj`（`official-code/config/default.yaml:85` 引用），配置中 `demonstrations:` 路径需替换。
- `README.upstream.md` 不含 CLI 运行命令，只有指向外部文档站的链接。

## 本地保存范围

`official-code/` 保存 `sweagent/` 包（agent、environment、tools、utils、run 入口）、`config/`（default、commands、swe_agent_ablations、ctf 变体、default_xml）、`README.upstream.md` 与 `LICENSE`。SWE-bench 评测 harness、`trajectories/`、`tests/`、`frontend/`、`api/` 与打包文件不在本目录中。

口径提示：`README.upstream.md` 自报 "resolves 12.47% of issues of the full test set and 23% of issues of SWE-bench lite"；其中 Lite 23% 晚于论文（论文为 18.00%），属后续版本口径。
