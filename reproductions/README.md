# 独立复现工作区

五位成员分别维护自己的 baseline 源码、benchmark 适配、配置、trace、运行状态、结果和说明。不得交叉引用其他成员的可写目录。

| 成员 | 工作区 | 开发分支 |
| --- | --- | --- |
| 周梦凡 | `zhouMF/` | `zhouMF/self-evolution-branch` |
| 赵星源 | `zhaoXY/` | `zhaoXY/self-evolution-branch` |
| 王懿 | `wangY/` | `wangY/self-evolution-branch` |
| 李永康 | `liYK/` | `liYK/self-evolution-branch` |
| 李嘉旺 | `liJW/` | `liJW/self-evolution-branch` |

每个成员目录固定包含 `H0/`、`GEPA/`、`meta-harness/`、`AutoSaddler/`。实验单元使用以下路径：

```text
reproductions/<成员>/<baseline>/<benchmark>/
├── configs/   # 可提交的运行配置
├── notes/     # 环境、命令、偏差与复现说明
├── results/   # 可提交的结果摘要；大体积原始产物不入库
├── runs/      # 本地运行状态，不入库
└── traces/    # 原始轨迹，不入库
```

自动优化 baseline 的官方源码放在 `<baseline>/code/`；H0 因 benchmark 而异，放在 `H0/<benchmark>/code/`。根目录 `benchmarks/` 只提供共享只读输入。
