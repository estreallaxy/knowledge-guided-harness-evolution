# Terminal-Bench 2.0 固定任务划分

| 文件 | 用途 |
| --- | --- |
| [`task-ids.txt`](task-ids.txt) | [上游任务提交 `69671fba`](https://github.com/harbor-framework/terminal-bench-2/tree/69671fbaac6d67a7ef0dfec016cc38a64ef7a77c) 中含 `task.toml` 的 89 个顶层目录名。 |
| [`generate_split.py`](generate_split.py) | 按固定 seed 和 SHA-256 排序生成任务划分；只读取任务 ID。 |
| [`split-v1.json`](split-v1.json) | 已冻结的 30 train / 19 dev / 40 test 清单。 |
| [`dataset/`](dataset/) | 上游固定提交的完整 89 题快照，随私有仓库分发；`UPSTREAM_PROVENANCE.json` 记录逐题哈希。 |
| [`vendor_dataset.py`](vendor_dataset.py) | 用上游 Git checkout 逐题核验仓库中的快照并生成来源记录。 |
| [`prepare_dataset.py`](prepare_dataset.py) | 检查上游 checkout 或已核验的仓库快照，复制为独立的 train/dev/test 数据集目录，并校验每题文件哈希。 |

用 `python generate_split.py` 复核清单；若现存 JSON 与生成结果不同，脚本会失败。该清单**复用** [AutoSaddler](https://arxiv.org/html/2608.23041) 的划分规模，**不是**它的同一随机划分。所有方法的优化器只看 train 任务和完整 trace，dev 仅供选择候选，test 到最终评估才运行。仓库快照与固定上游提交逐题比对；正式实验从快照生成本地 train/dev/test 目录，再由 Harbor `-p` 运行，记录镜像 digest 和结果；完整模型与预算协议见[第一阶段决定](../../docs/phase1-decisions.md)。

仓库拉取后的数据准备命令（只复制数据，不运行模型或评分；在仓库根目录执行）：

```bash
python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \
  --source benchmarks/terminal-bench-2.0/dataset \
  --output "$(dirname "$PWD")/benchmarks/tb2-split-v1"
```

输出中的 `train/`、`dev/`、`test/` 都是标准的 Harbor 本地任务集，可分别用 `harbor run -p <目录>` 读取。`dataset-manifest.json` 保存来源提交、划分哈希和每题内容哈希；再次运行命令只核验，不覆盖现有文件。优化器运行容器只挂载 `train/`，不要挂载完整上游 checkout、`dev/` 或 `test/`。

**服务器准备记录（2026-09-28）：**上游 checkout 位于 `/data1/users/zhangXY/benchmarks/terminal-bench-2`，提交为 `69671fbaac6d67a7ef0dfec016cc38a64ef7a77c`；核对 89 个任务均有 `task.toml`、`instruction.md` 和 `tests/test.sh`。`/data1/users/zhangXY/benchmarks/tb2-split-v1` 已生成并通过两次文件哈希核验，分别包含 30/19/40 题。上游 checkout、dev、test 目录仅 `cc` 可读，train 目录供成员读取。仓库快照让其他成员能在自己的目录创建相同数据集；运行优化器时仍只挂载 train。**尚未拉取任务镜像、启动 Harbor 或运行任何模型；这是数据就绪记录，不是评测结果。**
