# ExpeL 报告结果与复核边界

固定论文 `2308.10144v3`，原文定位：§4.1–4.3 / PDF pp.3–5；Algorithms 1–3 / p.6；Table 2 / p.9；Table 3 / p.10。

Table 2：ALFWorld 首次尝试 ReAct+Reflexion 40.3%、ExpeL retrieve only 54.5%、ExpeL+Reflexion 59.0%。首次尝试列消除了当前题重试贡献，但训练阶段仍使用 Reflexion。59.0−54.5 的差额支持规则组件价值；59.0−40.3 不能全部归因于规则维护。原版规则提取与执行模型不同，全部离线提炼成本本轮未知。

固定代码与本地适配的历史核对说明：论文术语为 UPVOTE/DOWNVOTE，固定代码 agent/expel.py 使用 AGREE/REMOVE。update_rules 先 REMOVE→AGREE→EDIT→ADD，文本子串识别已有规则，list_full 时 REMOVE 减 3，并按票数降序排序。本地改编采用论文基本票数规则、稳定 ID 和输入顺序，不实现满表 −3、上游文本解析/重排、Reflexion 采样。故不能称代码逐行复现或等价实现。

官方测试的执行结果：未知；没有运行完整上游系统。固定 README 中的官方入口保存在 [配置与示例](configs-and-examples.md)。此前独立本地适配通过 5 项合成功能测试；这些测试既不是官方测试，也不是 H0 迁移、收益或完整论文复现。
