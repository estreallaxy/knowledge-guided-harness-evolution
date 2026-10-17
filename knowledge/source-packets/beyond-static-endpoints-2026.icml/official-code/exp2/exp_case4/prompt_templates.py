"""Case4 prompt text and expected outcome notes."""

CASE4_USER_PROMPT = """请完成以下任务：
将本地 bench_seed/ 目录中的 5 个文档上传到 MinIO 的 incoming/ 前缀下。
列出 incoming/ 下的所有对象，并逐个下载检查其文本内容。
根据文档内容进行分类处理：
如果内容同时包含 invoice 和 paid，则复制到 processed/finance/ 目录。
如果内容包含 refund 或 claim，则移动到 processed/followup/ 目录，同时在 Memos 中创建一条新 memo，标题为 [FOLLOWUP] + 原文件名。
如果内容包含 draft 或 review，则移动到 processed/review/ 目录。
否则跳过（对象保持在 incoming/）。

处理完成后，完成验证。
"""

CASE4_EXPECTED = {
    "finance": ["invoice_paid_1.txt"],
    "followup": ["refund_case_1.txt", "invoice_claim_1.txt"],
    "review": ["draft_note_1.txt"],
    "incoming_keep": ["general_note_1.txt"],
}
