# AgentScope 1.0 报告结果与复核边界

固定论文 `2508.16279v1`，原文定位：§3.1.4 / PDF pp.10–11；固定 v1.0.0 的 _agent_base.py、_agent_meta.py。

原文与固定代码证明 reply/observe/reasoning/acting/print 的 pre/post 接口存在；没有可独立量化的 hook 成功率或成本消融。整套框架表现不能归给回调机制。

固定代码与本地适配的历史核对说明：固定版本 async_wrapper 的实例 hook 先于类 hook，pre 参数与 post 参数/输出都 deepcopy，post 在 original_func 正常返回后执行。本地保留该关键行为，增加通用函数 wrapper 和显式 shared registry，支持 bound function 与位置参数重绑定；不是安装 AgentScope，也没有用新版本 middleware 倒推旧接口。

官方测试的执行结果：未知；没有运行完整上游系统。固定 README 中的官方入口保存在 [配置与示例](configs-and-examples.md)。此前独立本地适配通过 5 项合成功能测试；这些测试既不是官方测试，也不是 H0 迁移、收益或完整论文复现。
