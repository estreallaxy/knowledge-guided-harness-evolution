# Terminal-Bench 2.0 固定任务划分

| 文件 | 用途 |
| --- | --- |
| [`task-ids.txt`](task-ids.txt) | [上游任务提交 `69671fba`](https://github.com/harbor-framework/terminal-bench-2/tree/69671fbaac6d67a7ef0dfec016cc38a64ef7a77c) 中含 `task.toml` 的 89 个顶层目录名。 |
| [`generate_split.py`](generate_split.py) | 按固定 seed 和 SHA-256 排序生成任务划分；只读取任务 ID。 |
| [`split-v1.json`](split-v1.json) | 已冻结的 30 train / 19 dev / 40 test 清单。 |
| [`prepare_dataset.py`](prepare_dataset.py) | 检查上游 checkout 的提交与 89 题清单，复制为独立的 train/dev/test 数据集目录，并校验每题文件哈希。 |

用 `python generate_split.py` 复核清单；若现存 JSON 与生成结果不同，脚本会失败。该清单**复用** [AutoSaddler](https://arxiv.org/html/2608.23041) 的划分规模，**不是**它的同一随机划分。所有方法的优化器只看 train 任务和完整 trace，dev 仅供选择候选，test 到最终评估才运行。正式实验需从固定上游提交的本地任务 checkout 通过 Harbor `-p` 运行，记录镜像 digest 和结果；完整模型与预算协议见[第一阶段决定](../../docs/phase1-decisions.md)。

服务器 `cc` 的数据准备命令（只复制数据，不运行模型或评分）：

```bash
python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \
  --source /data1/users/cc/benchmarks/terminal-bench-2 \
  --output /data1/users/cc/benchmarks/tb2-split-v1
```

输出中的 `train/`、`dev/`、`test/` 都是标准的 Harbor 本地任务集，可分别用 `harbor run -p <目录>` 读取。`dataset-manifest.json` 保存来源提交、划分哈希和每题内容哈希；再次运行命令只核验，不覆盖现有文件。优化器运行容器只挂载 `train/`，不要挂载完整上游 checkout、`dev/` 或 `test/`。

**服务器准备记录（2026-09-27）：**`/data1/users/cc/benchmarks/terminal-bench-2` 已检出上游提交 `69671fbaac6d67a7ef0dfec016cc38a64ef7a77c`，核对 89 个任务均有 `task.toml`、`instruction.md` 和 `tests/test.sh`。`/data1/users/cc/benchmarks/tb2-split-v1` 已生成并通过两次文件哈希核验，分别包含 30/19/40 题。上游 checkout、dev、test 目录仅 `cc` 可读，train 目录供成员读取。**尚未拉取任务镜像、启动 Harbor 或运行任何模型；这是数据就绪记录，不是评测结果。**
