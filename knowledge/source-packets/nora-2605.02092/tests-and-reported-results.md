# NORA 报告结果与复核边界

固定论文 `2605.02092v1`，原文定位：§4.1–4.3 / PDF pp.12–13；附录 E / pp.73–74；原始 settings.json 与 pre/post/stop 脚本。

附录 E 是同一 research brief 的定性去组件分析，不能给出独立 hook 增益、可靠恢复率或故障注入统计。论文 §4.1 的意外终止不丢状态主张超出当前公开 Stop 代码可证明的边界。保留为可审计的生命周期编排案例。

固定代码与本地适配的历史核对说明：固定原配置 Bash matcher 且以 $CLAUDE_TOOL_INPUT 作 argv；pre 脚本 regex 与 exit 1、无 deny JSON。2026-10-10 Claude Code 官方协议命令事件来自 stdin JSON，plain-text/空 stdout 的 exit 1 是非阻断错误；需要 exit 2 或有效决定字段。Stop 原脚本顺序复制/写文件不具多文件原子性。本地版本修正输入/决定合同，只做显式单文件交接，不复制原 permissions、通知或模型配置。固定上游树未找到 LICENSE：原始片段仅作本地来源证据，复用/再分发许可未知；runtime 是本地独立实现。

官方测试的执行结果：未知；没有运行完整上游系统。固定 README 中的官方入口保存在 [配置与示例](configs-and-examples.md)。此前独立本地适配通过 5 项合成功能测试；这些测试既不是官方测试，也不是 H0 迁移、收益或完整论文复现。NORA 的真实宿主 hook 接线未验证。
