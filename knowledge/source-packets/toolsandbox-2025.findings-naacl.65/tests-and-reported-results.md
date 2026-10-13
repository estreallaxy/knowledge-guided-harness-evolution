# Tests and reported results

## 论文报告结果

以下数值均为**论文结果，非本仓库复跑结果**；引用位置见 `exact-source-anchors.md`。

### 主结果：平均相似度（Table 5，PDF p.7 / p.1166）

列为：Avg Score、Single Tool Call、Multiple Tool Call、Single User Turn、Multiple User Turn、State Dependency、Canonicalization、Insufficient Information。

| 模型 | Avg | STC | MTC | SUT | MUT | SD | C | II |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4o-2024-05-13 | 73.0 | 87.8 | 80.1 | 84.2 | 74.7 | 84.0 | 76.6 | 42.0 |
| Claude-3-Opus-20240229 | 69.2 | 83.5 | 70.0 | 74.5 | 67.2 | 74.5 | 71.1 | 57.3 |
| GPT-3.5-Turbo-0125 | 65.6 | 93.4 | 73.9 | 81.8 | 66.6 | 82.6 | 70.4 | 22.3 |
| GPT-4-0125-Preview | 64.3 | 89.1 | 69.0 | 74.4 | 68.6 | 69.2 | 65.2 | 33.6 |
| Claude-3-Sonnet-20240229 | 63.8 | 82.1 | 66.2 | 69.1 | 69.7 | 84.5 | 65.5 | 44.2 |
| Gemini-1.5-Pro-001 | 60.4 | 82.6 | 49.8 | 63.1 | 37.3 | 70.5 | 51.6 | 76.2 |
| Claude-3-Haiku-20240307 | 54.9 | 80.9 | 54.2 | 64.3 | 46.0 | 69.5 | 54.4 | 39.4 |
| Gemini-1.0-Pro | 38.1 | 68.7 | 21.6 | 36.5 | 14.6 | 39.3 | 18.2 | 65.5 |
| Hermes-2-Pro-Mistral-7B | 31.4 | 63.3 | 18.3 | 29.9 | 18.6 | 27.1 | 19.9 | 48.3 |
| Mistral-7B-Instruct-v0.3 | 29.8 | 48.1 | 9.5 | 20.1 | 7.9 | 19.5 | 6.1 | 76.8 |
| C4AI-Command-R-v01 | 26.2 | 52.6 | 12.7 | 23.0 | 12.7 | 3.1 | 18.0 | 47.8 |
| Gorilla-Openfunctions-v2 | 25.6 | 36.2 | 8.2 | 15.1 | 9.3 | 0.0 | 8.9 | 69.2 |
| C4AI-Command R+ | 24.7 | 57.2 | 13.6 | 24.3 | 15.2 | 4.0 | 19.4 | 35.3 |

同一张表的工具增强列（0/3/10 干扰工具、All Tools、工具名/工具描述/参数描述/参数类型打乱）为：GPT-4o 75.1/75.0/74.6/72.6/72.4/69.3/73.0/71.9；Claude-3-Opus 68.3/68.6/70.0/67.5/70.8/71.5/65.8/71.1；其余模型见 PDF p.7。

论文从该表给出的结论：开源与闭源模型存在 >20 分的差距；Insufficient Information 与其他类别负相关（弱模型因"不乱调用"而虚高，论文明确称之为 side effect 而非正面结果）；State Dependency 上大模型反而劣于中等模型，原因是它们更倾向于对依赖工具发起并行调用；MTC/MUT 的退化速度远快于 STC/SUT（PDF pp.7–8）。

### 效率：平均轮数（Table 11，PDF p.24 / p.1183）

| 模型 | Avg Turn Count ↓ | 模型 | Avg Turn Count ↓ |
| --- | ---: | --- | ---: |
| Claude-3-Opus-20240229 | 11.6 | Gemini-1.5-Pro-001 | 15.0 |
| Mistral-7B-Instruct-v0.3 | 11.8 | Hermes-2-Pro-Mistral-7B | 15.3 |
| GPT-4o-2024-05-13 | 12.2 | Gorilla-Openfunctions-v2 | 24.2 |
| Gemini-1.0-Pro | 12.2 | C4AI-Command-R-v01 | 29.7 |
| Claude-3-Sonnet-20240229 | 12.4 | C4AI-Command R+ | 30.0 |
| GPT-4-0125-Preview | 13.0 | | |
| Claude-3-Haiku-20240307 | 13.6 | | |
| GPT-3.5-Turbo-0125 | 13.7 | | |

表注明确：轮数不能孤立解读，模型可能自信地做错并提前结束，应与相似度接近的模型互相比较。

### 消融与对照

| 实验 | 结果 | 位置 |
| --- | --- | --- |
| 用户模拟器提示（User Goal → +Knowledge Boundary → +Demonstration） | 幻觉 12.4 → 7.75 → 6.97；指令遵循错误 6.20 → 3.88 → 0.77（%，1032 条人工标注轨迹） | Table 2，PDF p.4 |
| 用户模拟器误差 vs agent | GPT-4o 8.02±1.36、Claude-3-Opus 7.78±0.52、Gemini-1.5-Pro 8.07±1.03（4 次重复 × 1032 轨迹的总错误率） | Table 3，PDF p.4 |
| ReAct 提示 vs 最小提示 | GPT-4o 73.0→73.6、Claude-3-Opus 69.2→69.3、GPT-4-0125 64.3→65.2、Claude-3-Sonnet 63.8→63.7 | Table 9，PDF p.22 |
| 模型功能覆盖 | Gorilla、Command-R 系列不能消费工具响应，理论上只能在 Single Tool Call 上得分 | Table 10，PDF p.23 |
| 工具 schema 打乱 | 论文报告为逐模型差异（Claude-3-Sonnet 在 All Tools 上比 0 干扰工具掉近 10 分；GPT-4o 对工具描述打乱敏感；Gemini-1.5 对参数类型打乱敏感） | §4，PDF p.8 |

### 基准规模与里程碑覆盖

| 基准 | 平均轮数 | 平均工具调用 | 测试用例 | 工具数 |
| --- | ---: | ---: | ---: | ---: |
| TOOL SANDBOX | 13.9 | 3.80 | 1032 | 34 |
| BFCL | 2.00 | 0.78 | 2000 | 1193 |
| ToolEval | 7.53 | 1.46 | 1625 | 3917 |
| API-Bank | 3.88 | 2.04 | 261 | 73 |
| ToolTalk | 7.42 | 3.68 | 78 | 28 |
| τ-bench | 29.33 | 4.48 | 165 | 24 |

（Table 4，PDF p.5）

场景类别计数（Table 6，PDF p.19，一个场景可属多类）：SINGLE_TOOL_CALL 152、MULTIPLE_TOOL_CALL 656、SINGLE_USER_TURN 584、MULTIPLE_USER_TURN 224、STATE_DEPENDENCY 192、CANONICALIZATION 472、INSUFFICIENT_INFORMATION 224。Table 7/8（同页）给出按数据库列（如 SETTING.wifi 136、SETTING.low_battery_mode 120）与按工具（如 `get_current_timestamp` 296、`search_contacts` 168）的里程碑覆盖计数。

## 官方检查入口

| 检查对象 | 官方代码 | 本地是否执行 |
| --- | --- | --- |
| 里程碑 / 矿场相似度算法 | `official-code/tests/common/evaluation_test.py`（4 个测试） | 已执行，4 项通过 |
| 世界状态快照、增删改与序列化 | `official-code/tests/common/execution_context_test.py`（13 个测试） | 已执行，全部通过 |
| 执行环境（语法错误、异常、并行调用） | `official-code/tests/roles/execution_environment_test.py`（6 个测试） | 已执行，4 通过 2 失败，见下 |
| 状态依赖工具行为 | `official-code/tests/tools/setting_test.py`、`messaging_test.py`、`contact_test.py`、`reminder_test.py`、`utilities_test.py` | 已执行，全部通过（RapidAPI 测试被跳过） |
| 消息与工具 schema 转换 | `official-code/tests/common/message_conversion_test.py`、`tool_conversion_test.py`、`tool_discovery_test.py`、`utils_test.py`、`validators_test.py` | 已执行，全部通过 |
| 场景解析 | `official-code/tests/cli/cli_test.py` | 已执行，通过 |
| 端到端评测产出 | `tool_sandbox` CLI 写出的 `result_summary.json`、`trajectories/*/conversation.json` | 未执行（需模型 API key 与 RapidAPI key） |

## 当前核验状态

| 项目 | 状态 | 证据等级 |
| --- | --- | --- |
| 论文全文可解析 | 已通过：`paper/paper-v1.txt` 含 `PDF p.1`–`p.24` 共 24 页标记，与会议页码 1160–1183 对应 | 本地运行（文本层） |
| 官方 PDF | 未纳入本包（原文件 20.2 MB，超出仓库体积约定）；获取地址 <https://aclanthology.org/2025.findings-naacl.65.pdf> | 未知（未做 PDF 解析复核） |
| 论文 §2–§4、§7、Appendix A.7、Table 2–9 与本地全文 | 已逐段与 `paper/paper-v1.txt` 核对 | 本地运行 |
| 官方代码版本 | 固定为 upstream revision `c8571d7` | 本地运行 |
| 官方单元测试 | 已执行：69 通过、2 失败、1 跳过（62 秒） | 本地运行 |
| 其中 2 项失败 | `tests/roles/execution_environment_test.py::test_execution_environment_syntax_error` 与 `::test_invalid_parallel_tool_call`，详见下节 | 本地运行 |
| 官方端到端评测复跑（模型 × 1032 场景） | 尚未执行；需 OpenAI / Anthropic / RapidAPI 凭据与较长时间预算 | 尚未执行 |
| 论文表格数值 | 已按原文誊录，未独立复算 | 论文报告 |
| 迁移到目标 Harness 的收益 | 尚未验证 | 尚未验证 |

### 本地复跑命令与结果

```bash
# 依赖按 official-code/pyproject.toml 的固定版本装入独立目录，未污染仓库
python3 -m pip install --target /tmp/tsdeps "polars==0.20.31" "networkx==3.2.1" \
  "numpy==1.26.4" "scipy==1.13.1" "rouge-score==0.1.2" "StrEnum==0.4.15" \
  "typing_extensions==4.12.2" attrs pytest decorator==5.1.1 tqdm \
  "dill==0.3.8" "jsonschema==4.19.2" "phonenumbers==8.13.39" "rapidfuzz==3.9.3" \
  "pyyaml==6.0.1" "requests==2.32.3" "pint==0.23" "ccy==1.3.1" "geopy==2.4.1" \
  "holidays==0.51" "pydantic==2.7.4" "tree-sitter==0.22.3" "tree-sitter-languages==1.10.2" \
  "langchain-core==0.1.30" "openai==1.17.0" "anthropic==0.26.1" "transformers==4.41.2" \
  "tokenizers>=0.19,<0.20" "vertexai==1.49.0" "sentencepiece==0.2.0"

PYTHONPATH=/tmp/tsdeps python3 -m pytest tests/ -q -o addopts=""   # Python 3.10.12
# => 2 failed, 69 passed, 1 skipped in 62.05s
```

跳过的一项：`tests/tools/rapid_api_search_tools_test.py`，模块级 `pytest.skip`（无 `RAPID_API_KEY`）。

两项失败的定位（均为本地复跑观察到的**代码行为**，不是论文结论）：

| 失败测试 | 现象 | 判断 |
| --- | --- | --- |
| `test_execution_environment_syntax_error` | 该测试把 Python 3.9 的 SyntaxError 提示原样写成期望值（单个 `^`），而 Python 3.10 会对整个 token 画 `^^^^` | 环境/解释器版本差异，与本包机制无关；换 3.9 解释器即可 |
| `test_invalid_parallel_tool_call` | `df[-2]["openai_function_name"]` 实际为 `set_wifi_status`，测试期望 `search_stock`。实现（`execution_environment.py:192-224`）在第一个排列就检测到失败时**直接返回该排列的响应**，而不是测试期望的置换后顺序；测试第 280 行的"wifi 应仍为关闭"断言之所以通过，是因为它读的是置换前捕获的 `ExecutionContext` 对象 | 官方测试的期望与实际实现存在顺序语义差异；论文 Appendix A.6 只声明"检测到竞态就一定发生"，未规定消息顺序，故不能据此否定论文结论 |

需要区分证据等级的两点：论文的"并行调用会被惩罚"属于**论文报告**；上面第 2 条只是**本地复跑观察到的代码行为**，两者不冲突但也不互相印证。

另有一处**代码与论文正文的差异**（不涉及失败）：`ScenarioCategories` 枚举定义了 `COREFERENCE` 与 `DISAMBIGUATION`，但论文 §3 与 Table 5 均未单列这两类，且全仓无任何引用（见 `exact-source-anchors.md`）。
