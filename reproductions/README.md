# 独立复现工作区

四位成员分别维护完整的 Meta-Harness 复现目录。`code/` 来自对[官方 Meta-Harness 仓库](https://github.com/stanford-iris-lab/meta-harness)的完整原生克隆；导入时移除了上游 `.git`，现在由本仓库及各自开发分支管理。每个目录包含独立代码副本、H0、配置、说明和本地运行路径；成员之间不得交叉引用代码、配置或运行产物。

| 成员 | 独立工作区 | 开发分支 |
| --- | --- | --- |
| 周梦凡 | `zhouMF/meta-harness/` | `zhouMF/self-evolution-branch` |
| 赵星源 | `zhaoXY/meta-harness/` | `zhaoXY/self-evolution-branch` |
| 王懿 | `wangY/meta-harness/` | `wangY/self-evolution-branch` |
| 永康 | `yongK/meta-harness/` | `yongK/self-evolution-branch` |

仅以下内容共享：`benchmarks/terminal-bench-2.0/` 的只读数据、评测协议、模型要求和结果字段定义。个人代码修改、依赖环境、配置、缓存、trace 与结果均留在本人的工作区。
