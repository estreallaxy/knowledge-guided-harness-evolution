# 团队执行范围

五位成员并行维护方法知识和独立复现实验。共同研究对象见 [research-plan.md](research-plan.md)，知识收集规则见 [knowledge/README.md](../knowledge/README.md)。

| 成员 | 知识工作 | 独立复现工作区 |
| --- | --- | --- |
| 周梦凡 | 指令与 Skill；上下文；模型选择 | `reproductions/zhouMF/` |
| 赵星源 | 工具；容错；执行循环 | `reproductions/zhaoXY/` |
| 王懿 | 多 Agent；运行观测与 Trace | `reproductions/wangY/` |
| 李永康 | 长期记忆；状态管理；扩展钩子 | `reproductions/liYK/` |
| 李嘉旺 | 规划；隔离与审批；验证与反馈 | `reproductions/liJW/` |

每位成员在自己的目录中维护 `H0/`、`GEPA/`、`meta-harness/`、`AutoSaddler/`。每组 baseline × benchmark 的配置、说明、trace、运行状态和结果均写入相应 benchmark 子目录；根目录 `benchmarks/` 仅作共享只读输入。
