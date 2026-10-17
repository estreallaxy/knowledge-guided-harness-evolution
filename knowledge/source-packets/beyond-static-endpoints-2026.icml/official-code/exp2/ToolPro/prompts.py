"""代码生成提示词：沿用 client_code_generator 的 Rust 约束风格；Go/Lua 为同任务下的变体。"""

from __future__ import annotations

from exp2.baseline.directus_tools import DIRECTUS_BASE_URL, TOOL_LIST_DOC


def _tool_block() -> str:
    return f"""
【实验环境 — Directus 基址】
{DIRECTUS_BASE_URL}
（生成示例 URL 或客户端配置时可引用；实际令牌由运行时注入，此处只要求逻辑与工具语义一致。）

【工具能力说明 — 与 exp2 Baseline 一致】
{TOOL_LIST_DOC}
"""


def build_generation_prompt_rust(task_user_text: str) -> str:
    tb = _tool_block()
    return f"""你是一个专家级 Rust 程序员，专门编写能够编译为纯 WebAssembly 的代码，注意绝对不能直接使用任何 return 语法的语句（在插入到 execute_internal 的片段中）。

⚠️ 重要警告：必须严格遵循以下约束，违反任何一条都会导致编译失败！

📌 【与下方「任务描述」文本的关系 — 必读，防协议混淆】
- 任务描述里若出现「每一轮只能输出 JSON」「action 为 tool_call / stop」「不得使用代码围栏」「输出 stop」等字样，来自 **Baseline 多轮 JSON 协议** 的固定前言，**在本实验中全部忽略**。
- **本实验的唯一交付物**：一段可编译的 Rust 源码，放在**一个** ```rust 围栏内；**不要**输出 tool_call/stop 的 JSON，不要把业务写成「回合 JSON」。
- 任务中「结束本轮（输出 stop）」应理解为：在逻辑末尾向 **已有的** `result` 写入说明即可，例如 `result.insert("reason".to_string(), serde_json::Value::String("...".to_string()));`，**不要**输出 `{{"action":"stop",...}}`。

⚠️ 重要警告（续）：嵌入位置与类型
- 你的片段插在 `execute_internal` 里、且位于**已经创建好的** `let mut result = HashMap::new();` **之后**；模板在片段结束后会**自动**写上 `Ok(result)` 收尾。
- **禁止**在用户片段里再写 `let mut result = ...`（尤其是 `serde_json::Map::new()`），否则会遮蔽外层 `HashMap` 并最终触发 **E0308（期望 `()` 或类型与 `HashMap` 不匹配）** 等错误。
- **禁止**在用户片段的「顶层」使用 `Ok(...)` / `Err(...)` 作为最后一条表达式（例如整段包在大括号里最后写 `Ok(result)`）。成功与失败信息一律通过 `result.insert("键", 值)` 写入；**不要**代替模板返回 `Result`。
- **禁止**用单独一对大括号 `{{ ... }}` 包裹**全部**业务代码并使块以 `Ok(...)` 结尾；应直接写多条语句（let / if / for / call_mcp_tool / result.insert），与模板中上下语句同一缩进层级。

- 代码插入到 execute_internal 函数体中，不写 main 函数
- 使用纯 WASM 环境，不使用 wasm-bindgen
- 必须使用 **外层** `result` 的 `result.insert(key, value)` 汇总输出，不要使用 return 语句
- 使用 call_mcp_tool(tool_name: &str, parameters: &serde_json::Value) 调用 MCP 工具（由宿主提供，与 ToolPro 一致）

{tb}

【任务描述 — 与 exp2/baseline/case_prompts 一致（请按上文「协议」一节解读）】
{task_user_text}

重要说明：
- 代码将被插入到 execute_internal 函数中
- 完全禁止 use 语句，所有类型显式路径或按模板已有导入使用（与项目编译模板一致）
- 不需要定义 main 函数或导出函数
- 直接编写业务逻辑代码
- 使用提供的 MCP 工具调用接口：call_mcp_tool(tool_name: &str, parameters: &serde_json::Value) -> Result<serde_json::Value, McpError>
- 生成的代码在语法中需要用到 return 的情景下都需要改为使用 result.insert，不要使用 result.success、result.error 等字段赋值
- 构造函数需要 String 类型而非 &str，例如 Value::String("字面量".to_string())
- 中间 JSON 可用 `serde_json::json!` / 临时 `serde_json::Map` 变量（**勿命名为 `result`**）；**对外汇总**必须写入外层的 `HashMap<String, serde_json::Value>`，即只用模板提供的 `result.insert`
- **最终状态**只通过 `result.insert` 表达；由模板统一 `Ok(result)`，用户片段内**不要** `Ok(result)` 收尾

🔧 【易编译失败点 — 必须遵守，来自真实 rustc 报错归纳】
1) **禁止**对 `call_mcp_tool(...)` **单独**使用 `?`  
   - `execute_internal` 的返回类型是 `Result<..., String>`，错误分支必须是 `String`。  
   - `call_mcp_tool` 返回 `Result<serde_json::Value, McpError>`，**不存在** `From<McpError> for String`，因此 **`call_mcp_tool(...)?` 会直接 E0277 编译失败**。  
   - **推荐写法**：`call_mcp_tool("工具名", &params).map_err(|e| e.to_string())?`  
     或使用完整 `match` / `if let Ok/Err`，在 `Err` 分支用 `result.insert` 写入说明并**不要再对 `McpError` 裸用 `?`**。
2) **禁止** `serde_json::Value::Number(浮点字面量.into())`（例如 `25.0.into()`）  
   - `f64` **不能** `.into()` 成 `serde_json::Number`，会触发 E0277。  
   - **推荐**：`serde_json::Value::Number(serde_json::Number::from_f64(25.0).unwrap())`；整数可用 `serde_json::Number::from(25i64)` 再包一层 `Value::Number(...)`。
3) **禁止** 在 JSON 数组迭代链里先用 `filter_map` 只保留 `&str`（如 `item["sku"].as_str()`），再在后续 `map` 里对「当前元素」做 `item["id"]`  
   - 经 `filter_map` 后迭代器元素已是 **`&str`**，不是 `serde_json::Value`；对 `str` 使用 `["id"]` 会报 **E0277（`str` cannot be indexed by `&str`）**。  
   - **推荐**：在闭包内仍拿着整条 `item: &serde_json::Value` 时同时判断 `sku` 并取 `id`，例如 `filter_map(|item| {{ ...; Some(item["id"].as_i64()?) }})`，或 `filter` + `filter_map` 全程不把元素变成纯字符串再回头索引。

📝 读写标记要求：
- 每个 call_mcp_tool 调用前添加 // @READ_OPERATION 或 // @WRITE_OPERATION

🚫 禁止：
- 直接 return 语句（在插入片段中；后处理会删除 return，易留半截代码）
- 比较 Result 与整数
- 臆造未在任务中出现的具体主键 id（应先 get_items 再使用返回数据中的 id）

请只输出一个 Markdown 代码围栏，语言标记为 rust，内含可插入 execute_internal 的完整片段。"""


def build_generation_prompt_go(task_user_text: str) -> str:
    tb = _tool_block()
    return f"""你是一个专家级 Go 程序员。生成**可读的、可静态审查**的 Go 代码，表达如何调用与下列工具语义等价的 Directus REST API（get_items → GET /items/{{collection}}；patch_item → PATCH；post_items → POST）。第一层评估会以 GOOS=wasip1 GOARCH=wasm 编译为 WASI WASM，须能通过 go build；**未使用的 import 即会导致失败**（见下文专节）。

【与任务正文的关系】任务描述里若要求「只输出 JSON」「action/stop」等，来自 Baseline 固定前言；**本实验忽略**，只输出 ```go 围栏内的 Go 源码。文中「输出 stop」表示业务完成即可，用注释或日志说明即可，不要交 JSON。

{tb}

【任务描述 — 与 exp2/baseline/case_prompts 一致】
{task_user_text}

要求：
- 使用标准库 net/http 或常见风格表达 HTTP 调用即可；可用占位符表示 Bearer Token。
- 根据任务分步：先查询 customers/orders/exchange_logs 等，再 patch/post；不得凭空写死业务 id，除非任务允许从查询结果链式得到。
- 读写标记（与 Rust 侧 MCP 约定一致，第一层会校验）：凡发起读类 HTTP 请求前添加注释行 `// @READ_OPERATION`；写类（POST/PATCH/PUT 等）前添加 `// @WRITE_OPERATION`（注释中须含字面子串 @READ_OPERATION 或 @WRITE_OPERATION）。
- 推荐输出完整 `package main` 与 `func main()`；若仅有片段，评估器会补上 `package main`（勿写多个 package）。
- 输出单一 ```go 代码围栏。

⚠️ 【Go 编译硬性规则 — 未遵守会直接 go build 失败，与业务逻辑无关】
- **禁止**在 `import (...)` 中列出**未在代码里实际引用**的包。Go 将「imported and not used」视为**错误**（非警告），典型报错形如：`"strconv" imported and not used`、`"strings" imported and not used`。
- **根源**：习惯性或复制粘贴 import 块（如 `strconv`、`strings`、`fmt` 等）却用 `fmt.Sprintf` 等替代了原计划用法时，会整段编译失败。
- **做法**：只保留确实调用了其导出符号的包；若某包未用，**必须从 import 中删除**。生成后 mentally 核对：每个 import 是否在源码中至少出现一次合法引用（类型、函数、常量等）。"""


def build_generation_prompt_lua(task_user_text: str) -> str:
    tb = _tool_block()
    return f"""你是一个专家级 Lua 程序员。生成**可静态审查**的 Lua 代码（可用 LuaSocket + luasec 或伪代码式 HTTP 表描述），表达与下列工具语义一致的 Directus 数据访问流程。

【与任务正文的关系】任务里「只输出 JSON」「stop」等为 Baseline 前言；**本实验忽略**，只输出 ```lua 围栏内脚本。「结束本轮」= 脚本逻辑执行完毕即可。

{tb}

【任务描述 — 与 exp2/baseline/case_prompts 一致】
{task_user_text}

要求：
- 步骤清晰：查询 → 根据返回再更新/创建。
- 不要凭空编造 id。
- 读写标记：读操作前 `-- @READ_OPERATION`，写操作前 `-- @WRITE_OPERATION`（须含字面子串 @READ_OPERATION 或 @WRITE_OPERATION）；凡代码中出现 HTTP/请求类调用时第一层会检查。
- 脚本须可被 gopher-lua `DoString` 一次执行（顶层可运行；避免依赖 Lua C 扩展）。
- 输出单一 ```lua 代码围栏。"""


def build_prompt(task_user_text: str, language: str) -> str:
    language = language.lower()
    if language == "rust":
        return build_generation_prompt_rust(task_user_text)
    if language == "go":
        return build_generation_prompt_go(task_user_text)
    if language == "lua":
        return build_generation_prompt_lua(task_user_text)
    raise ValueError(f"不支持的语言: {language}")


_LAYER1_COMPILE_ERROR_MAX = 16_000


def layer1_repair_system_message(language: str) -> str:
    """第一层编译失败后的纠错调用：模型只应输出一个代码围栏。"""
    lang = (language or "rust").strip().lower()
    if lang == "rust":
        return (
            "你是 ToolPro 第一层代码纠错助手。用户会给出原始任务、当前源码与完整编译/校验报错。"
            "你必须只输出一个 Markdown 代码围栏（语言标记 rust），围栏内为**完整可替换**的纠错后源码；"
            "禁止输出围栏外的任何解释、前言或后记。"
        )
    if lang == "go":
        return (
            "你是 ToolPro 第一层 Go 纠错助手。根据报错修复代码。"
            "只输出一个 ```go 围栏，内含完整可替换源码；围栏外不要有任何文字。"
        )
    if lang == "lua":
        return (
            "你是 ToolPro 第一层 Lua 纠错助手。根据报错修复脚本。"
            "只输出一个 ```lua 围栏，内含完整可替换源码；围栏外不要有任何文字。"
        )
    return (
        "你是代码纠错助手。只输出一个与首次生成相同语言的 Markdown 代码围栏，"
        "内含完整纠错后源码；不要输出围栏外的文字。"
    )


def build_layer1_compile_repair_prompt(
    task_user_text: str,
    language: str,
    broken_source_code: str,
    compile_error_text: str,
) -> str:
    """
    第一层编译/标记校验失败后的纠错 user 消息：任务 + 源码 + 报错。
    compile_error_text 过长时截断，避免撑爆上下文。
    """
    lang = (language or "rust").strip().lower()
    err = (compile_error_text or "").strip()
    if len(err) > _LAYER1_COMPILE_ERROR_MAX:
        err = (
            err[: _LAYER1_COMPILE_ERROR_MAX]
            + f"\n... [报错已截断，原长 {len(compile_error_text)} 字符]"
        )
    fence = {"rust": "rust", "go": "go", "lua": "lua"}.get(lang, lang)
    code = broken_source_code or ""
    return f"""以下代码已通过「首次生成」流程产出，但在第一层编译或静态校验（含读写标记等）时失败。

【原始任务需求 — 与首次生成相同】
{task_user_text}

【当前源码 — 请在此基础上纠错】
```{fence}
{code}
```

【完整报错 / 校验输出】
```
{err}
```

【纠错要求】
- 保持与首次生成**相同的交付形态**（Rust：可插入 execute_internal 的片段，遵守首次提示中的 MCP、result.insert、禁止裸 `?` 于 call_mcp_tool、读写注释等全部约束；Go/Lua：同首次生成的 package/标记约定）。
- 只修正导致失败的问题，不要无故重写无关逻辑。
- **输出**：仅一个 ```{fence} 围栏，内含纠错后的**完整**源码；不要其它 Markdown 段落。"""
