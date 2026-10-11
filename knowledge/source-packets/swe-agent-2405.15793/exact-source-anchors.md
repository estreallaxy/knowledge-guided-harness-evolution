# Exact source anchors

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| ACI 定义与动机（LM 是新一类终端用户；shell 缺小片段编辑、无无效编辑反馈） | §2，PDF p.2–3（Figure 1 p.1、Figure 2 p.2） | "we refer to the interface LM agents use to interact with computers as the agent-computer interface (ACI)"；shell "fails to provide simple commands to edit a small file segment, and does not provide any feedback if the user makes an invalid edit"。 |
| ACI 四条设计原则 | §2，PDF p.3（编号列表 1–4） | 命令简单、动作紧凑高效、反馈信息量足但简洁、guardrail 抑制错误传播（"Guardrails mitigate error propagation and hasten recovery"）。 |
| 窗口化文件查看：`open`、每次最多 100 行、带行号、省略行数提示、`scroll_up/down`、`goto` | §3 "File viewer"，PDF p.4；Table 4 p.17；§A.1 p.18（Figure 10） | "The file viewer presents a window of at most 100 lines of the file at a time"；显示全路径、总行数、前后省略行数与行号。 |
| 编辑命令：`edit <start>:<end>` + 替换文本（单区域、行范围）；编辑后自动刷新视图；linting guardrail 失败则丢弃编辑并报错 | §3 "File editor"，PDF p.4；§A.1 p.19–20（Figure 11 p.20） | "takes 3 required arguments: the start line, end line, and replacement text"；"Invalid edits are discarded, and the agent is asked to try editing the file again"；lint 输出存在时编辑被回滚（p.19）。注意：编辑是行范围而非 search/replace（"search-and-replace" 仅作为 No-edit 基线里 sed 的描述出现）。 |
| 反馈设计：无输出时显式提示、格式错误重试模板、旧观测折叠（last 5） | §3 "Context management"，PDF p.4；§A.1 Figure 30/31 p.43、Figure 32 p.44 | 无输出时 "Your command ran successfully and did not produce any output"；"observations preceding the last 5 are each collapsed into a single line"。 |
| 主结果：SWE-bench full/Lite、RAG / Shell-only / SWE-agent 对照 | §5 + Table 1，PDF p.5–6 | SWE-agent w/ GPT-4 Turbo 12.47%（full）/18.00%（Lite）；Claude 3 Opus 10.46%/13.00%；Shell-only GPT-4 Turbo Lite 11.00%（w/o demo 7.33）；RAG 1.31/3.79。 |
| ACI 组件消融（编辑器 × 检索 × 窗口 × 上下文），SWE-bench Lite | §5.1 + Table 3，PDF p.5–6（Figures 5/6 p.7） | w/ linting 18.0 vs edit action 15.0 vs No edit 10.3；Summarized 18.0 vs Iterative 12.0 vs No search 15.7；100 行 18.0 vs 300 行 14.3 vs 整文件 12.7；Last-5 18.0 vs Full history 15.0 vs w/o demo 16.3。 |
| 超参扫描与 per-repo/年份细分 | §B.1 Table 5 p.25；§B.2 Table 6–7 p.25–26 | GPT-4 Turbo 最佳 15.1%（T=0.0/窗口 100/Last-5，dev 子集 37 例）；2024-11 代码下 0.0/200 仅 9.2–10.8%；按仓库 django 26.32%、sympy 10.39%。 |
| 限制/边界 | §E.3 Limitations & Future Work，PDF p.117–118；§A.1 p.19–20 | "The final SWE-agent configuration has a small toolkit"；"the ACI development process and case studies are done manually"；"the scope of SWE-agent is exclusively focused on programmatic tasks"；guardrail "forces some edits to be done in a particular order"。 |

检索上限口径差（论文 vs 快照代码）：论文 §3 p.3–4 与 §A.1 p.20 称检索结果 "at most 50"/"50 or fewer"，而快照代码在 **>100** 才拒绝（`official-code/config/commands/search.sh:41` 文件数、`:102` 命中行数）。属论文完成时（2024 年中）与 2024-11 revision 的漂移。

## 官方代码

快照自报 `__version__ = "0.7.0"`（`official-code/sweagent/__init__.py:5`）。注意：本 revision 已把命令全部迁移为 `config/commands/*.sh` 的 bash 函数，Python 侧没有 OpenCommand/EditCommand 之类的类（`grep -rn 'OpenCommand|EditCommand|do_edit|lint' --include=*.py` 零命中）；同节内后续路径省略 `official-code/` 前缀。

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| 窗口化查看：`_print` 输出 `[File: … (N lines total)]`、行号、省略行数提示，head/tail 取 `$WINDOW` | `official-code/config/commands/defaults.sh:1-13` | 实现论文 §3 的 100 行窗口 + 行号 + lines above/below。 |
| `open` 命令（line_number、越界警告、目录/文件不存在提示、经 `_constrain_line` 居中后 `_print`） | `config/commands/defaults.sh:15-25, 39-80`（docstring 27-38） | ACI 的 open 接口本体；`WINDOW` 默认值见 `config/default.yaml:88`。 |
| 滚动/跳转：`goto`、`scroll_down`、`scroll_up` 与连续滚动告警 | `config/commands/defaults.sh:90-121`（goto）、`123-140`（告警）、`145-170`（scroll） | 对应论文 §3 窗口移动与"检索优先"引导。方向以代码 `CURRENT_LINE ± (WINDOW-OVERLAP)`（:151, :166）为准（论文 Table 4 p.17 的 scroll 描述与实现相反）。 |
| edit 主流程：flake8 选择码 → 备份 → 写回 → 比对 lint 差异 → 通过则 `_print`；有错则打印两段并回滚 | `config/commands/edit_linting.sh:1-6`、`49`（`--select=F821,F822,F831,E111,E112,E113,E999,E902`，与论文 p.19 逐字一致）、`64-71`、`74-80`、`83-88`（接受）、`90-129`（拒绝，`:127` "Your changes have NOT been applied…"） | 论文 §3/§A.1 的 linting guardrail。 |
| 命令定义/文档注入/多行命令解析（生成 `{command_docs}`） | `sweagent/tools/commands.py:12-19`、`78-138`（parse_bash_functions）、`172-227`（ParseCommandDetailed） | 支撑论文 §A.3：命令文件→提示中的命令文档。 |
| 工具安装与状态：command_files 注入容器 `/root/commands`；env_variables 导出（WINDOW/OVERLAP/CURRENT_LINE/CURRENT_FILE） | `sweagent/tools/tools.py:53-79`（ToolConfig，`:78` 自动 `pip install flake8`）、`138-215`（ToolHandler.install/_install_commands/_set_env_variables） | 论文 §A.3 配置四要素中的 Command files / Environment variables。 |
| 反馈与重试：格式错误模板 → 追加临时历史重问；`exit_context/exit_cost` 退出标记 | `sweagent/tools/parsing.py:65-121`（ThoughtActionParser，`:75-84` error_message）、`sweagent/agent/agents.py:415-431`（retry_after_format_fail）、`452-494`（check_format_and_requery） | 对应论文 Figure 32 与 §3 格式错误重试。 |
| 主循环 & 上下文管理：`step()`/`run()`；旧观测折叠为一行 `Old output omitted (n lines)`；`last_n_observations n:5` | `sweagent/agent/agents.py:621-668, 671-699`；`sweagent/agent/history_processors.py:31-53, 56-68`；`config/default.yaml:113-115`；`sweagent/environment/swe_env.py:163-205` | 论文 §3 历史折叠 + Figure 31。 |
| 运行入口与数据集：CLI run / run-batch / run-replay；`SWEBenchInstances(flavor=lite/verified/full)` → HF `princeton-nlp/SWE-Bench[_Lite|_Verified]`；Docker 镜像 `swebench/sweb.eval.x86_64.<iid>:v1` | `sweagent/run/run.py:13-46`；`sweagent/run/run_batch.py:24-43, 78-100, 106-121`；`sweagent/run/batch_instances.py:203-243, 123-135`；`sweagent/environment/config/deployment.py:33-47` | 论文 §4 数据集/评测入口的代码对应。 |

行号以 `source-packet.json` 固定的官方代码 revision 为准。
