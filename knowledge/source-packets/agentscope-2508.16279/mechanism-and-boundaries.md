# 实例与类生命周期回调的输入输出合同

AgentScope 的生命周期 hook 允许扩展行为而无需直接修改核心方法。固定 v1.0.0 实现定义了回调顺序、参数复制和返回值更新语义；这些接口事实不等于 hook 组件的性能收益。

| 字段 | 机制说明 |
| --- | --- |
| 目标瓶颈 | 日志、校验和行为扩展直接侵入 agent 核心代码，难以独立组合 |
| 作用模块 | 生命周期扩展注册与异步方法包装 |
| 输入 | hook 类型与名称、回调函数、方法参数、原方法输出 |
| 触发条件 | 被包装方法执行前/正常返回后；回调需已注册 |
| 必要步骤 | 注册实例或类回调；规范化参数；按序执行 pre；调用原方法；按序执行 post；返回更新输出 |
| 状态变化 | 回调注册表增删；pre 可替换参数，post 可替换结果，None 表示不替换 |
| 预期输出 | 按回调合同更新后的方法输出，以及扩展自行保存的记录 |
| 前提与限制 | pre 返回值须满足参数字典合同；参数与输出 deepcopy 的兼容性、回调开销未知。原方法异常不进入正常 post，不能将 post 用作必达清理或崩溃恢复保障 |

## 机制与证据对应

| 标识 | 主张 | 论文与固定代码 | 支持范围 |
| --- | --- | --- | --- |
| AS1 | 生命周期 pre/post hook 可修改输入与输出 | PDF pp.10–11 §3.1.4；`_agent_meta.py:_wrap_with_hooks` | 支持论文接口设计与固定包装实现，不支持独立收益结论 |
| AS2 | 实例回调先于类回调，参数和结果复制后传入，None 不替换 | `_agent_meta.py:_wrap_with_hooks` | 固定代码的具体语义；论文没有逐项规定该顺序和复制合同 |
| AS3 | 注册同名 hook 会覆盖原回调；原方法异常不触发正常 post | `_agent_base.py:register_instance_hook`、`register_class_hook`；`_agent_meta.py:_wrap_with_hooks` | 固定代码行为；不能类推为 finally hook 或异常恢复能力 |

精确行号与范围哈希见 [证据映射](claim-evidence-map.json)。论文提及 reasoning/acting 等事件，但本包选定 `_agent_base.py` 与 `_agent_meta.py` 主要核对 reply/observe/print；未归档部分不补造实现位置。框架结果与 hook 消融边界见 [结果说明](tests-and-reported-results.md)。

## 方法关系与项目使用边界

- [NORA](../nora-2605.02092/mechanism-and-boundaries.md)：AS1–AS3 是进程内函数回调，NO1–NO2 是宿主命令事件与文件交接；触发时机、输入格式、异常和退出码合同不同，不能直接互换。
- [StateFork](../statefork-2609.38648/mechanism-and-boundaries.md)：可用 AS1 观察 SF1 的动作和消耗；这是待测接线，不提供物理恢复能力。

未来接入时需要单独验证回调失败语义、顺序和成本；当前未安装完整框架、未接入 H0，也未测迁移收益。不能因接口可核实而宣称整体框架收益由 hooks 带来。
