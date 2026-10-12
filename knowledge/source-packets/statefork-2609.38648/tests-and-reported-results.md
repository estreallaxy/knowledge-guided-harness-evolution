# StateFork 报告结果与复核边界

固定论文 `2609.38648v1`，原文定位：§2.2 状态边界；§3.1–3.3 / PDF pp.6–7；§4 Waypoint；§5.2 / pp.11–12；附录 A 评测条件。

论文报告相同 MCTS 与 visited-node 预算下任务完成相对提高约 26%、探索最高快约 70%；这是其 Terminal-Bench 设置、77 题且每配置一次，不是共同 TB2.0 30/19/40 协议。Smart Decider 对 eager：平均完成时间减少 23%、存储减少 58%，不是单项机制的本地迁移收益。

固定代码与本地适配的历史核对说明：论文估计 C_phys=αm+β，并与累计 C_replay 比较。固定 StateFork decider/decider.py 的 ThresholdDecider 默认 threshold=5 秒，并无此线性模型。本地版本由调用方显式传入估计成本，再按论文规则选择；不自动拟合 α/β，不宣称复现 upstream Smart Decider。Waypoint 固定代码为并发 fork 模型，需 Linux、root、CRIU/OverlayFS 与 fork-capable CLI；论文原实验 commit 未知，不能与论文后端自动等价。

官方测试的执行结果：未知；没有运行完整上游系统。固定 README 中的官方入口保存在 [配置与示例](configs-and-examples.md)。此前独立本地适配通过 5 项合成功能测试；这些测试既不是官方测试，也不是 H0 迁移、收益或完整论文复现。StateFork 的真实 CRIU/Waypoint 后端未验证。
