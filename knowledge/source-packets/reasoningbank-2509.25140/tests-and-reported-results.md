# ReasoningBank 报告结果与复核边界

固定论文 `2509.25140v2`，原文定位：§3.2 / PDF pp.4–5；附录 A.1–A.2 / pp.21–22；Table 1 / p.7；附录 C.2 / Table 5 / p.27。

Table 1：WebArena / Gemini-2.5-Flash，No Memory→ReasoningBank 成功率 40.5%→48.8%，平均步骤 9.7→8.3。Table 5：含 action generation、judge、extraction 的总 token 50,847.4→53,054.5，约 +4.3%。这是基础 ReasoningBank 系统结果，不混入 MaTTS，不是单条记忆的因果收益。

固定代码与本地适配的历史核对说明：原论文对测试任务流持续学习；本地改编只允许 declared train 更新，并在 dev/test 前冻结。固定代码 WebArena/memory_management.py 在导入时初始化 Vertex/GenAI 客户端；本地模块无云端初始化。judge/extractor 与 embedding 显式注入，费用由调用方累计。检索粒度、来源校验、JSON 冻结校验和均为本地变更。

官方测试的执行结果：未知；没有运行完整上游系统。固定 README 中的官方入口保存在 [配置与示例](configs-and-examples.md)。此前独立本地适配通过 5 项合成功能测试；这些测试既不是官方测试，也不是 H0 迁移、收益或完整论文复现。
