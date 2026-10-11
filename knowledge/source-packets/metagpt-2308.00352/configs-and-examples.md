# Configs and examples

## 官方配置

| 设置 | 配置目录 | 主要内容 |
| --- | --- | --- |
| 主配置样例 | `official-code/config/config2.yaml`、`official-code/config/config2.example.yaml` | `llm.api_key="YOUR_API_KEY"` 占位；运行时复制为 config2.yaml 并填充真实 key。 |
| 各家 LLM 样例 | `official-code/config/examples/`（9 个） | anthropic-claude-3-5-sonnet、aws-bedrock、google-gemini、groq-llama3-70b、huoshan_ark、openai-gpt-3.5-turbo、openai-gpt-4-turbo、openrouter-llama3-70b-instruct、spark_lite。 |
| 组件配置 | `official-code/metagpt/configs/`（11 个） | llm/browser/embedding/file_parser/mermaid/models/redis/s3/search/workspace 等配置项。 |

配置只能和对应论文版本、代码 revision 与模型环境一起解释。论文中的运行结果不能由单个 YAML 独立复现。

## 官方流程入口

官方 README（本包内为 `official-code/README.upstream.md`）核对过的命令：

```bash
# 安装（Python >=3.9,<3.12，见 README:64-66）
pip install --upgrade metagpt

# 生成配置后填入 API key
metagpt --init-config

# 运行示例
metagpt "Create a 2048 game"
```

或代码入口 `generate_repo("Create a 2048 game")`（README:107；`official-code/metagpt/software_company.py:16-78`）。运行产物落在 `./workspace`。

带可执行反馈的完整流程 = `run_tests=True` 雇佣 QaEngineer：

1. WriteTest 生成 `{workspace}/tests/test_*.py`；
2. RunCode 以 subprocess 运行 `python tests/…`（timeout=10s，`official-code/metagpt/actions/run_code.py:92-118`）；
3. 失败则 DebugError 重写代码并重试（至多 3 次与论文 §3.3 对应）。

运行前提：

- Python >=3.9,<3.12（README:64-66）。
- OpenAI 兼容 API key（`official-code/metagpt/configs/llm_config.py:46-58`；默认读 `./config/config2.yaml` 与 `~/.metagpt/config2.yaml`）。
- 快照不含 `metagpt/utils`、`tools`、`ext` 等被引用模块（`official-code/metagpt/team.py:24`、`official-code/metagpt/software_company.py:11` 引用 `metagpt.utils.*`），独立运行需完整安装上游包。
- HumanEval/MBPP 评测脚本与 harness 不在本快照（`grep -ri humaneval|mbpp` 零命中），论文复现需上游 `examples/benchmark`。

## 本地保存范围

`official-code/` 保存 `metagpt/` 核心包（team、roles 五角色、actions、environment 消息池、schema、configs）、`config/`（config2.yaml 占位与 9 个 LLM 样例）、`README.upstream.md`、`LICENSE`。上游的 utils/tools/ext、examples/benchmark、数据集与测试不在本目录中。
