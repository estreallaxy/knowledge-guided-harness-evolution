# ToolPro

ToolPro 是一个面向 LLM 智能体的可执行工具程序研究 artifact。它不让智能体把复杂任务拆成很多轮 API 调用，而是让模型生成带 READ / WRITE 效果标记的小程序，将程序编译到 WebAssembly，在 MCP 风格工具上执行，并用 replay / fallback 策略保守处理写操作。

本仓库同时包含论文主实验脚本，以及补充实验里的 ToolPro bench1-bench4 程序模式 runner。

## 先看这里

| 你的目标 | 建议入口 |
|---|---|
| 快速理解这个 artifact | [仓库里有什么](#仓库里有什么) |
| 跑补充实验 bench1-bench4 | [补充基准快速开始](#补充基准快速开始) |
| 跑论文主实验应用工作流 | [论文主实验](#论文主实验) |
| 找目录和模块 | [仓库结构](#仓库结构) |
| 排查配置问题 | [配置注意事项](#配置注意事项) |

英文版说明见 [README.md](README.md)。

## 仓库里有什么

ToolPro 有两条实验路径：

1. **论文主实验**：`experiment/calculate/`
   - 覆盖 Memos、Directus、MinIO 上的应用级工作流。
   - 适合看完整系统集成、调用流量和开销统计。

2. **补充 ToolPro 基准**：`exp2/ToolPro/`
   - 覆盖 bench1-bench4 的程序模式评测。
   - 流程是：模型生成代码 -> 第一层编译门闸 -> Wasm 执行 -> validator 校验。
   - 如果你想直接看“可执行工具程序”这一思路，建议从这里开始。

仓库主要能力包括：

- 工具工作流代码生成。
- Rust / Go / Lua 第一层编译检查。
- WebAssembly 执行与宿主侧 MCP 风格调用。
- READ / WRITE 效果标记。
- replay-aware repair 和保守 fallback。
- Directus / MinIO / Memos benchmark validators。

## 仓库结构

| 路径 | 作用 |
|---|---|
| `core/` | 执行引擎、编译管线、Wasm runtime、replay、fallback、history |
| `client/` | 客户端代码生成与 route selection |
| `services/` | 查询和维护辅助模块 |
| `experiment/calculate/` | 论文主实验脚本 |
| `experiment/mcp-server/` | 主实验使用的 MCP 风格 server 和 tool bridge |
| `experiment/mcp-client/` | MCP client 配置与会话代码 |
| `exp2/ToolPro/` | 补充实验 ToolPro CLI 和程序模式 benchmark runner |
| `exp2/baseline/` | stepwise baseline、任务 prompt、Directus seed/init、validators |
| `exp2/exp_case4/` | Case 4 相关资产：Directus + MinIO + Memos |
| `ToolPro_Experiment/` | Directus、MinIO、Memos 的 Docker Compose 示例 |

## 环境要求

- Python 3.10+
- Rust toolchain，并安装 `wasm32-unknown-unknown`
- Docker，用于 Directus / MinIO / Memos
- 可选：Go 1.21+，仅 Go / Lua 第一层路径需要
- `exp2.ToolPro` 需要 OpenRouter 兼容模型接口

## 安装

```bash
git clone https://github.com/morgen52/toolpro_icml26.git
cd toolpro_icml26

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
rustup target add wasm32-unknown-unknown
```

Windows PowerShell 中激活环境：

```powershell
.\venv\Scripts\Activate.ps1
```

## 环境变量

在仓库根目录创建 `.env`，不要提交密钥。

补充 ToolPro runner 需要：

```text
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

主服务 / 主实验客户端栈需要：

```text
LLM_API_KEY=...
LLM_MODEL=...
LLM_BASE_URL=...
SERVER_URL=http://localhost:8001
```

`exp2.ToolPro` 当前读取 OpenRouter 兼容变量。如果使用其他厂商，可以把 `OPENROUTER_BASE_URL` 指向兼容网关，或修改 `exp2/ToolPro/llm_client.py`。

## 补充基准快速开始

这是运行 ToolPro 程序模式 artifact 的最直接路径。

### 1. 启动依赖服务

Cases 1-3 需要 Directus。Case 4 还需要 MinIO 和 Memos。

`ToolPro_Experiment/` 下有示例 Compose 文件：

```bash
docker compose -f ToolPro_Experiment/directus-docker/docker-compose.yml up -d
docker compose -f ToolPro_Experiment/docker-minio/docker-compose.yml up -d
docker compose -f ToolPro_Experiment/memos/docker-compose.yml up -d
```

### 2. 初始化 / 检查服务

在仓库根目录执行：

```bash
python -m exp2.baseline init
python -m exp2.exp_case4.test.test_init_services
```

如果只跑 Cases 1-3，Case 4 的服务检查可以跳过。

### 3. 运行 ToolPro

```bash
python -m exp2.ToolPro --language rust --model env --batches 1 --cases 1,2,3,4
```

`--cases all` 等价于 `1,2,3,4`。加 `-v` 会打印模型原始回复、抽取源码、READ / WRITE 标记、编译输出和执行细节。

结果目录：

- 混合运行和 Cases 1-3：`exp2/ToolPro/results/`
- 部分 Case 4-only 运行：`exp2/exp_case4/results/`

每个 run 会打印 `[PASS/FAIL]`；完整四个 benchmark 跑通时，应能看到 Cases 1-4 都至少有一次 PASS。

## Benchmarks

| Bench | 仓库 case | 核心挑战 |
|---|---|---|
| bench1 | Case 1 | 运行时检索正确 pending order，然后做绑定写入 |
| bench2 | Case 2 | 循环、分支、协同写入 |
| bench3 | Case 3 | 非幂等状态修改和 exchange log 创建 |
| bench4 | Case 4 | 跨 MinIO、Directus、Memos 的工作流和清理 |

任务 prompt 与校验逻辑主要在 `exp2/baseline/case_prompts.py`、`exp2/baseline/validator.py` 和 `exp2/exp_case4/`。

## 论文主实验

论文主实验路径在 `experiment/calculate/`。

运行前需要：

- 启动所需 Docker 服务。
- 配置 `experiment/mcp-server/settings.toml`。
- 如 MCP client 设置不同，配置 `experiment/mcp-client/`。
- 使用完整 client/server 栈时，启动 `start_server.py` 和 `start_client.py`。

启动可选主服务：

```bash
python start_server.py
python start_client.py
```

运行完整应用级脚本：

```bash
cd experiment/calculate
python application_test_with_dw.py
```

运行较轻量的流量统计工作流：

```bash
cd experiment/calculate
python test_refactored.py --test 1 --batch 5
```

主实验结果默认写到 `experiment/calculate/results/`。

## 常用 CLI 参数

| 目标 | 参数 |
|---|---|
| 选择语言 | `--language rust`、`--language go`、`--language lua` |
| 使用 `.env` 里的模型 | `--model env` |
| 选择 cases | `--cases 1,3` 或 `--cases all` |
| 只编译不执行 | `--skip-execute` |
| 打印详细日志 | `-v` |
| 开关 replay | `--replay on` / `--replay off` |
| 修改 fallback policy | `--fallback-policy safe_stepwise` / `fail_fast` |
| 模拟额外 RTT | `--extra-rtt-ms <毫秒>` |
| 修改客户端预检 | `--client-precheck strict|warn|off` |

完整 CLI 说明见 `exp2/ToolPro/README.md`，也可运行：

```bash
python -m exp2.ToolPro --help
```

## 配置注意事项

- Directus 配置必须一致。`exp2/baseline/directus_tools.py` 中有写死的 Directus URL/token 默认值，initializer、runner、validator 必须指向同一个实例。
- Case 4 默认配置在 `exp2/exp_case4/config.py`。
- `ToolPro_Experiment/` 是方便起步的 Compose 示例，不是唯一部署方式。
- 除非明确做消融，不要对非确定性写使用 replay，例如 `--replay-allow-nondeterministic-writes`。
- 如果生成程序无法安全 replay，ToolPro 的设计是保守 fallback，而不是夸大 replay 保证。

## Smoke Checks

```bash
python -m exp2.ToolPro --help
```

安装依赖并启动服务后，可以用下面几个命令检查服务相关路径：

```bash
python -m exp2.exp_case4.test.test_init_services
python test_write_mode_debug.py --help
python test_memos_rollback_mechanism.py --help
```

多数实验检查依赖本地服务与密钥。只改文档时，可以先用 `git diff --check` 做快速 sanity check。

## 背景

ToolPro 把外部 API 交互视为表示层问题。静态 tool endpoint 往往迫使智能体在 prompt 状态里维护控制流，并进行多轮 stepwise 调用。ToolPro 则生成带显式 READ / WRITE 效果的可执行工具程序，在 Wasm 沙箱中执行，并围绕 repair 使用 replay / fallback 策略。

这不同于主要把代码当内部草稿的 code-as-planning 工作：这里的生成程序就是对外 API 表面上的动作表示。它也不同于 GraphQL 或服务端批处理，因为它不依赖预声明工作流族的固定 schema。
