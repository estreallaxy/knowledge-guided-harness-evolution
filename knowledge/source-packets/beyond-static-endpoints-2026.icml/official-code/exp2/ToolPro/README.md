# ToolPro 实验脚本

在 **exp2 Baseline 同款任务描述**（`exp2/baseline/case_prompts.py`）下，让 LLM **生成代码**（而非多轮 tool JSON），并用 **第一层（读写标记 + WASM 编译）** 统计效果。工具能力说明来自 **exp2** 的 `directus_tools.TOOL_LIST_DOC`（与 Baseline 一致的三项工具：`get_items` / `patch_item` / `post_items`）。

Rust 提示词约束对齐 `client/client_code_generator.py`（`execute_internal` 片段、`call_mcp_tool`、`result.insert`、读写注释等）；Go / Lua 为同一任务下的语言变体提示词。

## 环境依赖

- 项目根目录 `.env`（与 Baseline 相同）：
  - `OPENROUTER_API_KEY`
  - `OPENROUTER_MODEL`（默认生成模型，交互菜单中可选「使用 .env 默认」）
  - `OPENROUTER_BASE_URL`（默认 `https://openrouter.ai/api/v1`）
- **第一层 — Rust**：`cargo` + `wasm32-unknown-unknown`，走 `core.compilation_engine.CompilationEngine`（与主工程一致）。
- **第一层 — Go**：Go **1.21+**，`go` 在 PATH；`GOOS=wasip1 GOARCH=wasm` 编译 WASI 组件；首次 `go mod tidy` 需能访问模块代理以下载依赖。
- **第一层 — Lua**：同样依赖 **Go 1.21+**；脚本经 **yuin/gopher-lua** 嵌入临时 `main.go`，先 `go run`（加载/执行 Lua）再 `go build` 产出 WASI WASM。
- Python 依赖：仓库已有包（`httpx`、`python-dotenv` 等）。

## 如何开始测试

1. 在项目根目录准备好 `.env`（`OPENROUTER_API_KEY`、`OPENROUTER_MODEL`、`OPENROUTER_BASE_URL`）。  
2. 若跑 Rust / Go / Lua 第一层编译，按上文安装 **cargo** 或 **go** 等工具链。  
3. 在**仓库根目录**执行下面任一方式。

### 交互式（推荐首次使用）

```bash
python -m exp2.ToolPro
```

无参数时会依次询问：语言、生成模型、批次数、Case 范围，以及**是否在终端详细打印每步**（原始回复、抽取源码、读写标记、WASM 编译）。若语言选 **Go**，会再问第二层执行后端（wasip1_wasmtime / rust_wasm_core，与 `--go-execution-backend` 一致）。  
结束后终端会打印 **=== ToolPro 汇总 ===**（总次数、正确率、总耗时、按批次/Case 统计），并写入 `exp2/ToolPro/results/{时间戳}_toolpro.json`。同一次会话内 **`{时间戳}_toolpro_terminal.txt`** 会保存**完整标准输出**（UTF-8），与 JSON 共用同一时间戳；恢复真实终端后会再打印一行「终端完整日志已保存: …」。

### 命令行（可脚本化）

```bash
# 使用 .env 中的 OPENROUTER_MODEL，Rust，1 批次，全部 Case
python -m exp2.ToolPro --language rust --model env --batches 1 --cases all

# 指定 OpenRouter 模型 id
python -m exp2.ToolPro --language rust --model openai/gpt-4o --cases 1,3

# 终端打印每步详情（原始回复、源码、标记、编译）
python -m exp2.ToolPro --language rust --model env -v --cases 1

# 结果目录（默认 exp2/ToolPro/results）
python -m exp2.ToolPro --log-dir exp2/ToolPro/results

# 编译前客户端轻检（默认 strict：失败则跳过真实 WASM 编译）
python -m exp2.ToolPro --language rust --model env --cases 2 --client-precheck strict
python -m exp2.ToolPro --client-precheck warn   # 仅记录，不挡编译
python -m exp2.ToolPro --client-precheck off

# 消融：放宽 §3.2.7 下 nondeterministic WRITE 的 replay 策略（传入 WasmRuntime；默认关闭）
python -m exp2.ToolPro --language rust --model env --cases 1 --replay-allow-nondeterministic-writes

# Go 第二层：默认 wasip1；与 Rust 共用 SeparatedExecutionEngine 时需内嵌 Rust 片段（见 README「Go + rust_wasm_core」）
python -m exp2.ToolPro --language go --model env --cases 1 --go-execution-backend rust_wasm_core
```

每条 run 会生成 **`intent_instance_id`**（UUID）并传入执行引擎；结果 JSON 的 `runs[]` 含 `client_precheck_passed` / `client_precheck_failures`（`off` 时为 `null`）、`replay_allow_nondeterministic_writes`、`go_execution_backend` 及执行回显 `replay_allow_nondeterministic_writes_engine`。会话级 `config` 含 `client_precheck`、`replay_allow_nondeterministic_writes`、`go_execution_backend`。

### Go：`rust_wasm_core` 与 Rust 共用 ``SeparatedExecutionEngine``（M4）

- CLI：`--go-execution-backend wasip1_wasmtime`（默认）或 `rust_wasm_core`。
- 选 `rust_wasm_core` 时，在 Go 文件**块注释**中嵌入与 Rust ToolPro 模板一致的 **execute_internal 体**片段，用以下标记包裹（放在 `package main` 之前即可）：

```text
/* TOOLPRO_RUST_GUEST_BEGIN
result.insert("smoke".to_string(), serde_json::json!({"via":"rust_core"}));
Ok(result)
TOOLPRO_RUST_GUEST_END */
```

- 第一层仍对 Go 做 wasip1 编译门闸；第二层改为走 ``execute_rust_with_core_engine``（与 Rust 相同宿主 MCP / replay 参数）。

### 终端默认会打印什么？

| 模式 | 内容 |
|------|------|
| **默认（非 verbose）** | 每个 run 一行摘要 `[PASS/FAIL] batch=… case=… compile=…`；失败时简短 `compile` 节选；**最后整块「ToolPro 汇总」**（与 JSON `aggregate` 一致）。 |
| **verbose（`-v` 或交互选是）** | 每个 run 内：**①** 模型原始回复 **②** 抽取后源码 **③** 读写标记结果 **④** WASM 编译 backend/success/体积/耗时；最后同样是 **汇总**。 |

完整原文与代码始终写入结果 JSON（`runs[].raw_llm_response`、`extracted_source_code` 等），终端 verbose 仅为便于实时查看。

交互菜单中可选的**代码生成模型**（与需求一致）：

- `.env` 默认 `OPENROUTER_MODEL`（如 `qwen/qwen3-max`）
- `openai/gpt-4o`
- `google/gemini-3-flash-preview`
- `anthropic/claude-sonnet-4.6`

## 评估逻辑

**读写标记 + 编译为 WASM**（流程仿照 CompilationEngine 的「临时工程 + 子进程」）：

- **标记校验**（先于编译，对齐 `client_code_generator`）：若存在 `call_mcp_tool(`（Rust）或检测到典型 HTTP/请求调用（Go/Lua），源码中须出现 **`@READ_OPERATION` 或 `@WRITE_OPERATION`**（通常为 `// @READ_OPERATION` / `// @WRITE_OPERATION` 或 Lua 的 `-- …`）。  
- **Rust**：`compile_rust_to_wasm`，嵌入主工程 `lib.rs` 模板，`wasm32-unknown-unknown`。  
- **Go**：`core.go_wasip1_compiler` 临时模块后 `go build`（WASI）；第一层实现与 ToolPro 共用。产物为 **WASI wasm**，与主工程 Rust 的 `wasm32-unknown-unknown` 宿主导入不同。  
- **Rust（第二层）**：`run_toolpro` 在未 `--skip-execute` 时用 `SeparatedExecutionEngine` 进程内执行 + `validate_case`。  
- **Go（第二层）**：`go_wasip1` wasm 在 **Wasmtime + WASI**（`core.wasip1_runner`）中调用 ``_start``，程序内 `net/http` 等走 WASI；随后 `validate_case`（**direct-to-Wasm**，与 rebuttal Q1 表述一致）。  
- **Lua**：`lua_gopher_wasip1.py` 将用户脚本 Base64 嵌入 gopher-lua shim，宿主 `go run` 后再 `go build` WASI wasm。  

结果 JSON 中 `compile_backend`：`rust_compilation_engine` | `go_wasip1` | `lua_gopher_wasip1`；`wasm_bytes_length` 为产出体积（字节）。Go/Rust 在跑通执行阶段时另有 `execution_backend`：`rust_wasm_core` | `go_wasip1_wasmtime`。

**单次 run 是否通过**：第一层须成功；Rust / Go 在未 `--skip-execute` 时尚需 `validation_passed`；Lua 仍以第一层编译为准。

- 默认写入目录：`exp2/ToolPro/results/`
- 文件名：`{时间戳}_toolpro.json`；同次运行另有 **`{时间戳}_toolpro_terminal.txt`**（本次所有 `print` 到标准输出的完整副本，UTF-8）。
- 汇总字段与 `exp2/baseline/run_baseline_test.py` 风格一致，包括：
  - `aggregate.total_wall_seconds`（全会话墙钟时间）
  - `aggregate.average_seconds_per_run` / `average_seconds_per_batch`
  - `aggregate.accuracy`（通过 run / 总 run）
  - `aggregate.by_case`（分 Case 正确率与平均评估耗时）
- 每条 run 另含：`compile_backend`、`wasm_bytes_length`、`generate_seconds`、`compile_seconds`、`compile_passed`、`compile_error`、完整任务提示与模型原始输出（过长会截断）。

## 模块说明

| 文件 | 作用 |
|------|------|
| `prompts.py` | 按语言拼接工具说明 + `case_prompts` 任务正文 |
| `llm_client.py` | OpenRouter 兼容 `chat/completions` |
| `code_extract.py` | 从模型输出中提取围栏代码 |
| `wasm_compile_check.py` | 第一层统一入口：`compile_first_layer_to_wasm` |
| `wasm_compilers/tool_markers.py` | `@READ_OPERATION` / `@WRITE_OPERATION` 第一层校验 |
| `wasm_compilers/go_wasi.py` | 重导出 `core.go_wasip1_compiler`（兼容旧 import） |
| （主工程）`core/wasip1_runner.py` | Go wasip1 wasm：Wasmtime `define_wasi` + `_start` |
| `wasm_compilers/lua_gopher_wasip1.py` | Lua → gopher-lua shim → WASI wasm |
| `go_rust_guest_extract.py` | 从 Go 源解析 ``TOOLPRO_RUST_GUEST_*`` 供 ``rust_wasm_core`` 执行 |
| `program_execution.py` | Rust / Go 第二层：``execute_rust_with_core_engine``、``run_go_program_execution_sync`` |
| `client_interface_precheck.py` | 编译前轻检：Case 端点覆盖、循环骨架、读写顺序（Rust/Go 启发式） |
| `run_toolpro.py` | 交互 / CLI、批跑、写结果；`--client-precheck`、`--go-execution-backend` |

## 与 Baseline 的差异

- Baseline：多轮 JSON `tool_call` + Directus 真执行 + 数据库 `validator`。  
- ToolPro：**单次代码生成** + 第一层 **按语言的 WASM 编译门闸**；Rust 与 Go 在未 `--skip-execute` 时还会经第二层执行（Rust = core ``execute`` WASM；Go = **默认** wasip1 wasm 在 Wasmtime 内 `_start`，**或** ``--go-execution-backend rust_wasm_core`` 时走与 Rust 相同的 core 引擎，见上文）并对 Directus 做 **`validate_case`**。Lua 仍为仅编译门闸。
