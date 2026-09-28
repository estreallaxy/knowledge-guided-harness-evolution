# 执行 harness

`h0/` 下每个子目录保存一个可独立运行的初始执行 harness；`candidates/` 保存从某个 H0 派生的可版本化候选实现。

| H0 | 来源 | 运行入口 | 核验状态 |
| --- | --- | --- | --- |
| [Terminus-KIRA](h0/terminus-kira/) | [Meta-Harness TB2 参考实现](https://github.com/stanford-iris-lab/meta-harness/tree/main/reference_examples/terminal_bench_2) | `agents.baseline_kira:AgentHarness` | 已保存上游参考实现；尚未运行 benchmark。 |

## Terminus-KIRA

[`h0/terminus-kira/`](h0/terminus-kira/) 原样保存 Meta-Harness TB2 参考实现中的初始 `agents/baseline_kira.py`、提示词、缓存辅助文件和 `pyproject.toml`。上游许可证保存在 [`LICENSE.upstream`](h0/terminus-kira/LICENSE.upstream)。这里不包含 Meta-Harness 搜索后发布的高分 agent。

运行时把 `h0/terminus-kira/` 放在 `PYTHONPATH` 上，导入 `agents.baseline_kira:AgentHarness`。提示词路径由实现相对于 `agents/` 解析为 `../prompt-templates/terminus-kira.txt`。不要直接修改 H0；候选应复制到独立目录并记录相对 H0 的差异。

任务侧 harness 尽量开放给优化器；benchmark 任务、评分器、运行器和封存测试数据始终在其可编辑边界之外。若扩展 `H0` 的能力，所有 baseline 必须从相同新版本重新运行。
