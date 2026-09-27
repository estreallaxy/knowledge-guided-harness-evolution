# Terminal-Bench 2.0 固定任务划分

| 文件 | 用途 |
| --- | --- |
| [`task-ids.txt`](task-ids.txt) | [上游任务提交 `69671fba`](https://github.com/harbor-framework/terminal-bench-2/tree/69671fbaac6d67a7ef0dfec016cc38a64ef7a77c) 中含 `task.toml` 的 89 个顶层目录名。 |
| [`generate_split.py`](generate_split.py) | 按固定 seed 和 SHA-256 排序生成任务划分；只读取任务 ID。 |
| [`split-v1.json`](split-v1.json) | 已冻结的 30 train / 19 dev / 40 test 清单。 |

用 `python generate_split.py` 复核清单；若现存 JSON 与生成结果不同，脚本会失败。该清单**复用** [AutoSaddler](https://arxiv.org/html/2608.23041) 的划分规模，**不是**它的同一随机划分。所有方法的优化器只看 train 任务和完整 trace，dev 仅供选择候选，test 到最终评估才运行。正式实验需从固定上游提交的本地任务 checkout 通过 Harbor `-p` 运行，记录镜像 digest 和结果；完整模型与预算协议见[第一阶段决定](../../docs/phase1-decisions.md)。
