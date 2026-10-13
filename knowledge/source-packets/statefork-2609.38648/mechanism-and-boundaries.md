# 逻辑分支与物理状态恢复的分离

StateFork 用逻辑节点表达 agent 的探索树，由后端决定节点采用真实检查点还是命令回放。Waypoint 是其中的执行会话后端，恢复范围和运行前提不能被逻辑层接口替代。

| 字段 | 机制说明 |
| --- | --- |
| 目标瓶颈 | 分支探索需要重复恢复前缀，纯回放昂贵，文件快照又可能遗漏进程与服务状态 |
| 作用模块 | 环境分支控制、检查点物化策略与执行会话后端 |
| 输入 | 活动会话、命令序列、父子节点、累计回放耗时、后端与检查点成本估计 |
| 触发条件 | 搜索请求 snapshot/restore/cleanup；snapshot 时决定物理或虚拟表示 |
| 必要步骤 | 创建逻辑节点；按策略物化或保存回放命令；恢复最近物理祖先；对虚拟节点回放后缀；维护节点关系和活动状态 |
| 状态变化 | 逻辑节点树及命令日志更新，物理检查点增加或清理，活动会话切换 |
| 预期输出 | 稳定节点标识、可恢复会话、执行观察和耗时/存储记录 |
| 前提与限制 | 回放必须能重建相关观察；外部服务不自动恢复。Waypoint 要求 Linux/root、CRIU、OverlayFS 等；当前本机后端未验证，运行器与环境修改也超出优化 agent 编辑边界 |

## 机制与证据对应

| 标识 | 主张 | 论文与固定代码 | 支持范围 |
| --- | --- | --- | --- |
| SF1 | 虚拟节点通过物理祖先加命令后缀恢复 | PDF p.6 §3.1–3.2；`controller/base_env_manager.py:_snapshot_branch`、`_restore_current_branch` | 支持公开逻辑层；代码回放非零退出仅记日志，因此返回成功不能单独证明观察等价 |
| SF2 | 论文比较物理成本与回放成本；固定代码使用默认 5 秒阈值 | PDF pp.6–7 §3.2；`decider/decider.py:ThresholdDecider` | 明确论文估计公式与固定实现差异；不能称阈值实现复现了论文线性成本模型 |
| SF3 | Waypoint 的会话恢复需要特定操作系统和后端能力 | PDF p.7 §4、p.12 §6；Waypoint `docs/INSTALL.md` 前提 | 论文范围与固定安装要求；实际后端可运行性、隔离性和本地成本未知 |
| SF4 | 固定 forkable manager 当前只支持物理快照 | `controller/forkable_env_manager.py:_validate_decider` | 公开代码约束；不能把逻辑层虚拟节点能力推广到该并发分支实现 |

精确定位见 [证据映射](claim-evidence-map.json)。系统收益、Smart Decider 成本结果及本地适配差异分别记录在 [结果边界](tests-and-reported-results.md)。固定代码不是论文实验 commit 的已核实对应版本。

## 方法关系与项目使用边界

- [AgentRewind](../agentrewind-2608.14380/mechanism-and-boundaries.md)：SF1/SF3 可与 AR2 比较恢复边界；逻辑控制接口有借鉴价值，文件恢复不能代替进程/会话恢复。
- [AgentScope](../agentscope-2508.16279/mechanism-and-boundaries.md)：AS1 的 pre/post hook 可记录 SF1 的分支动作与时间，作为适配设想；hook 注册不能提供检查点后端，也没有已验证组合收益。

条件保留为逻辑状态与物理状态分离的来源。当前只收集接口和边界，不部署后端，不修改共享运行器。回退必须保留累计消耗，不把失败回放或缺少外部状态静默算作可靠恢复。
