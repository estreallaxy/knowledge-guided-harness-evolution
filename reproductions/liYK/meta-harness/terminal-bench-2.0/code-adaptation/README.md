# 模型接线与训练入口

执行和优化固定使用 DeepSeek。`agents/` 的独立子类从本人的官方 `meta-harness/code/` 加载 KIRA，实现百炼接口接线；官方参考文件保持原样，不依赖其他成员工作区。

| 入口 | 用途 |
| --- | --- |
| `agents.deepseek_kira:AgentHarness` | 项目初始 harness（H0）的模型接线 |
| `agents.deepseek_candidate_003:AgentHarness` | 工具参数容错与思考续接候选 |
| `launch.py` | 数据准备、环境检查、train 评估与预览 |
| `propose.py` | 读取冻结训练证据、生成新候选；评估单独运行 |
| `import_history.py` / `export_train.py` | 核对、迁移或导出完整训练证据 |
| `with_service.py` | 从本机服务配置向子进程加载变量，不打印凭据 |

三个接线方法与冻结历史实现 AST 一致；候选文件与历史执行文件字节一致。模型、完整 reasoning_content 续接和预算由轻量配置记录。完整命令见 [运行说明](../README.md)。

[来源清单](provenance.json)、[接口核对](port-verification.json)和[历史差异](historical-adaptation.diff)保留源码起点及哈希。`historical-agents/`、`historical-tests/` 是来源材料，不是运行入口；沿用的历史文件名不代表本次模型选择。

18 项检查仅使用合成响应和模拟 provider。`verify_delivery.py` 核对本实验目录内 H0/候选摘要、任务集合、源码哈希和接线 AST。源码核对不等于真实行为等价性证明，当前入口没有新增 benchmark 试次。
