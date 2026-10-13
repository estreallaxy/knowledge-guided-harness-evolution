# AgentRewind 报告结果与复核边界

固定论文 `2608.14380v1`，原文定位：Framework / PDF pp.2–4；External Environment Recovery Boundary / p.4；Table 2 / p.6；附录 B–C 预算与实现说明。

Table 2：Terminal-Bench 2.0 Continue 78.7%、AgentRewind 83.1%。原协议没有预设总墙钟、步骤或 token 上限，且 rewind/重复提交可获得验收反馈，因此不能当作本项目固定预算、封存 test 下的提升。DeepSeek-V4-Flash 的 Continue 列不是该模型的 AgentRewind 增益。官方 alpha 明确不含私有 benchmark harness/数据。

固定代码与本地适配的历史核对说明：原版外置 bare Git/private index 追踪与恢复工作区；本地改编用文件副本与 SHA-256，只恢复到新目录。不实现 rewind monitor/自动选择、模型后缀生成或原版录制回放系统。保留累计 usage、显式边界声明、源不覆盖均是本地迁移设计，尚未接入 H0。

官方测试的执行结果：未知；没有运行完整上游系统。固定 README 中的官方入口保存在 [配置与示例](configs-and-examples.md)。此前独立本地适配通过 5 项合成功能测试；这些测试既不是官方测试，也不是 H0 迁移、收益或完整论文复现。
