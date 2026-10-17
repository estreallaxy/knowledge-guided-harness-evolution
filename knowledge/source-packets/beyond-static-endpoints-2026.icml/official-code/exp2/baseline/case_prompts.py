"""Case 用户消息：通用 MCP/输出规范片段 + 各 Case 纯业务逻辑描述（不含任何接口或参数细节）。"""

from __future__ import annotations

BASELINE_USER_PREAMBLE = """【MCP 能力与工具清单】
你已连接到一台 MCP 服务器。系统提示（system）中列出的每一个工具名称，均为该服务器侧已注册、可由你在本环境中通过 JSON 的 tool_call 调用的能力。选择工具时，将名称填入 "tool" 字段；具体入参放入 "arguments" 对象。各工具对应的后端能力类别、参数是否必填、字段含义与取值类型，以系统提示中的《工具说明书》为准；本段不给出 URL、路径模板或查询串写法等技术细节。

【如何理解工具执行结果】
每次工具调用结束后，你会收到一段 JSON 文本：通常包含本次请求的 HTTP 状态码（status_code）以及服务端返回体（body）。列表类结果中，记录数组多出现在 body.data；单条更新或创建的结果形态以实际返回为准。一切后续推理必须严格基于这些返回值中的字段，不得臆造未出现的内部标识符、主键或列表内容。

【回合输出规范】
每一轮你只能输出**一个**合法 JSON 对象：action 取 "tool_call" 或 "stop"；不得附加 Markdown、自然语言段落或代码围栏。若 action 为 "stop"，须包含简短字符串字段 "reason"。任务是否真正完成由系统在 stop 之后独立判定，与 reason 文案无关。
"""

# 仅描述「要达成什么」，不涉及如何调用接口或如何拼参数
CASE_LOGIC_ONLY: dict[int, str] = {
    1: """【任务】Case 1（动态发现标识后再写入）

在业务数据里找到「名为 Mei、姓为 Patel、邮编为 76165」的客户，并记下系统为该客户分配的内部标识（不得猜测或沿用常识中的假 id）。
在此基础上，找出属于该客户、且仍处于待处理状态的那批订单；从中确定需要操作的那一单，将其货品列表更新为**仅包含**货品编号 1096508426，并将该订单的金额总价调整为 55.0。其他订单与交换日志无需处理。

完成上述业务目标后结束本轮（输出 stop）。
""",
    2: """【任务】Case 2（批量地址、客户主地址联动与条件换货）

找到与 Case 1 相同身份特征的客户（Mei Patel，邮编 76165），记下其内部标识。
将该客户名下所有仍处于待处理状态的订单的收货地址，统一更新为「445 Maple Drive, New City」；并将该客户的主地址更新为同一地址。
随后关注订单号为 #W4082615 的订单：若其业务状态**不是**「已发货」，则将该订单的货品替换为仅含 new_simple_puzzle_999，并把订单总价改为 25.0；若已是已发货则按业务含义不应再按「未发货换货」路径处理。

【实现提示 · Directus】查询 customers 请使用 filter 字段组合：`first_name` `_eq` Mei、`last_name` `_eq` Patel、`zip_code` `_eq` 76165（勿使用不存在的单一 name 字段）。**必须**对该客户在 **customers** 集合执行一次更新，将字段 **`primary_address`** 写为「445 Maple Drive, New City」（勿只改 orders 的 `shipping_address` 而漏改客户主地址）。按订单号筛选时 `order_number` 须与系统记录完全一致（含开头的 `#`，例如 `#W4082615`）。

按上述逻辑处理完毕后结束本轮（输出 stop）。
""",
    3: """【任务】Case 3（已交付订单换货与交换日志）

针对订单号为 #D12345、在业务上处于已交付状态的那笔订单：将其推进为「换货已申请」类状态，并把货品更新为仅含 new_exchange_item_888。
同时在交换日志中新增一条记录：写明该订单号、换出前的货品集合（须与系统中该笔订单在数据层面记录的旧货品一致；在标准初始数据集下，旧货品对应包含 SKU 片段 old_delivered_item_456 的那组条目）、换入货品为 new_exchange_item_888。若需要先核对订单再写入，可先通过只读方式确认再执行写入。

【实现提示 · Directus】按订单号查询或写入关联字段时 `order_number` 须与系统记录完全一致（含 `#` 前缀，例如 `#D12345`）。对订单做 `patch_item` 时须使用列表接口返回的**真实主键 id**，不得猜测 id。订单的 `status` 字段须写入**英文枚举值** `exchange_requested`（与校验脚本一致）；**不可**写入中文描述（如「换货已申请」等），否则校验不通过。

完成后结束本轮（输出 stop）。
""",
    4: """【任务】Case 4（MinIO 文档分类 + Memos 联动 + 验证）

将本地 bench_seed/ 目录中的 5 个文档上传到 MinIO 的 incoming/ 前缀下。
列出 incoming/ 下的所有对象，并逐个下载检查其文本内容。
根据文档内容进行分类处理：
- 如果内容同时包含 invoice 和 paid，则复制到 processed/finance/ 目录。
- 如果内容包含 refund 或 claim，则移动到 processed/followup/ 目录，同时在 Memos 中创建一条新 memo，标题为 [FOLLOWUP] + 原文件名。
- 如果内容包含 draft 或 review，则移动到 processed/review/ 目录。
- 否则跳过（对象保持在 incoming/）。

处理完成后完成验证。

【实现提示 · MinIO/Memos】若通过 bench 种子类工具将文件落到可读路径，则对每个需出现在 MinIO 的对象须调用上传类工具并在 arguments 中传入**完整文件正文**（字节或文本），不得发出无正文的空上传。**`minio_upload_object` 的 arguments 必须同时包含 `object_name` 与 `content`**；缺少 `content` 时服务端可能返回 200 但对象为空，后续分类校验会失败。**`minio_list_objects` 成功时 `body` 为对象，对象键列表在 `body.objects`（字符串数组），另有 `body.count`；勿将 `body` 当作 JSON 数组。** **`minio_get_object` 成功时正文在 `body.content`（字符串），勿将 `body` 当作整段 UTF-8 字符串。** 列出与下载后的解析须与上述字段一致。Memos 中跟进类 memo 的标题须以 `[FOLLOWUP]` 开头并拼接原文件名（与上文任务描述一致）。
""",
}


def get_case_user_prompt(case_id: int) -> str:
    if case_id not in CASE_LOGIC_ONLY:
        raise ValueError(f"未知 Case: {case_id}")
    return (
        BASELINE_USER_PREAMBLE.strip()
        + "\n\n---\n\n"
        + CASE_LOGIC_ONLY[case_id].strip()
    )
