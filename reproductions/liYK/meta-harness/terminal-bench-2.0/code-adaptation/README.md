# Meta-Harness KIRA 百炼适配与历史来源

`agents/` 是针对 main `88efe13` 官方 KIRA 快照的独立子类，供应商接线没有修改 `meta-harness/code/` 中的官方文件。`agents/__init__.py` 从本人的 `meta-harness/code/reference_examples/terminal_bench_2/agents/` 加载官方实现，不依赖其他成员或本机历史副本。

| 入口 | 用途 |
| --- | --- |
| `agents.deepseek_kira:AgentHarness` | KIRA 的百炼兼容子类，模型和思考策略见 `../configs/deepseek-api.json`。 |
| `agents.deepseek_candidate_003:AgentHarness` | 历史候选 003 的原样代码，处理命令参数与输出截断后的思考内容续接。 |

适配把 `_call_llm_for_image`、`_call_llm_with_tools`、`_handle_llm_interaction` 三个历史兼容方法放入子类；三者与冻结历史实现的 AST 一致。供应商参数与构造流程沿用历史 Qwen 接线，改为读取本 benchmark 的 DeepSeek 配置。官方原生 run loop、解析器和总结流程继续继承；候选源码与历史文件字节一致。

## 检查入口

使用官方 `../code/reference_examples/terminal_bench_2/pyproject.toml` 的 Python 3.12 依赖；本次环境为 Harbor 0.18.0、LiteLLM 1.84.10、Tenacity 9.1.4。从 `reproductions/liYK/meta-harness/terminal-bench-2.0/` 执行：

```bash
PYTHONPATH=code-adaptation:../code/reference_examples/terminal_bench_2 python -m unittest discover -s code-adaptation/tests -v
python code-adaptation/verify_delivery.py
```

13 项检查通过：8 项历史候选检查与 5 项接线、模型约束和官方快照检查。检查只使用合成响应和模拟 provider，不需要密钥，不调用模型或 benchmark。`verify_delivery.py` 用标准库核对摘要计数、两路 task ID、历史文件哈希和移植来源。

配置只记录 `BAILIAN_API_KEY` 和 `BAILIAN_OPENAI_COMPATIBLE` 的变量名；凭据由调用方加载。真实执行需要 Harbor/容器、任务和外部凭据，现有 `configs/experiment.json` 是历史条件记录，不是完整任务启动配置。

## 证据边界

[历史差异](historical-adaptation.diff) 对应固定兼容参考 commit `8123ccabe2b19fa1123090b2e5f1bacc20963ce8`；[历史来源](provenance.json) 和 [移植核对](port-verification.json) 分别保留原执行来源与本次改动。`historical-agents/`、`historical-tests/` 保持原样，不能作为新目录下的直接入口。

历史 train 的 13/30、17/30 来自原执行源码，不来自本次移植后的代码。历史 H0 是 KIRA 百炼适配版；新版 `H0/terminal-bench-2.0/code/` 保存 Terminus，历史结果不能冒充 Terminus 对照。完整行为等价性、移植后的真实任务运行和共同协议符合性仍未验证。独立 dev 未完成，test 和第二轮搜索未开展。
