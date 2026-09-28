# Terminal-Bench 2.0 固定任务划分

| 文件 | 用途 |
| --- | --- |
| [`task-ids.txt`](task-ids.txt) | [上游仓库](https://github.com/harbor-framework/terminal-bench-2)中含 `task.toml` 的 89 个顶层目录名。 |
| [`generate_split.py`](generate_split.py) | 按固定 seed 生成任务划分；只读取任务 ID。 |
| [`split-v1.json`](split-v1.json) | 已冻结的 30 train / 19 dev / 40 test 清单。 |
| [`dataset/`](dataset/) | 上游完整 89 题快照，随私有仓库分发；`UPSTREAM_PROVENANCE.json` 保存来源记录。 |
| [`vendor_dataset.py`](vendor_dataset.py) | 用上游 Git checkout 逐题核验仓库中的快照并生成来源记录。 |
| [`prepare_dataset.py`](prepare_dataset.py) | 检查上游 checkout 或仓库快照，复制为独立的 train/dev/test 数据集目录，并核对任务完整性。 |

用 `python generate_split.py` 复核清单；若现存 JSON 与生成结果不同，脚本会失败。该清单**复用** [AutoSaddler](https://arxiv.org/html/2608.23041) 的划分规模，**不是**它的同一随机划分。所有方法的优化器只看 train 任务和完整 trace，dev 仅供选择候选，test 到最终评估才运行。正式实验从仓库快照生成本地 train/dev/test 目录，再由 Harbor `-p` 运行，记录环境版本和结果。

仓库拉取后的数据准备命令（只复制数据，不运行模型或评分；在仓库根目录执行）：

```bash
python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \
  --source benchmarks/terminal-bench-2.0/dataset \
  --output "$(dirname "$PWD")/benchmarks/tb2-split-v1"
```

输出中的 `train/`、`dev/`、`test/` 都是标准的 Harbor 本地任务集，可分别用 `harbor run -p <目录>` 读取。`dataset-manifest.json` 保存来源和任务清单；再次运行命令只核验，不覆盖现有文件。优化器运行容器只挂载 `train/`，不要挂载完整上游 checkout、`dev/` 或 `test/`。

**服务器准备记录（2026-09-28）：**上游 checkout 位于 `/data1/users/zhangXY/benchmarks/terminal-bench-2`；核对 89 个任务均有 `task.toml`、`instruction.md` 和 `tests/test.sh`。`/data1/users/zhangXY/benchmarks/tb2-split-v1` 已生成，分别包含 30/19/40 题。仓库快照让有仓库读取权限的成员在各自目录创建相同数据集；运行优化器时只挂载 train。由于完整 89 题已推送到共享私有仓库，dev/test 的保密性不能依靠服务器目录权限保证；若实验要求严格盲测，应由独立评测方保管未公开的测试题。**尚未拉取任务镜像、启动 Harbor 或运行任何模型；这是数据就绪记录，不是评测结果。**
