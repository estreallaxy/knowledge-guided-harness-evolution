"""
实验用 MCP 工具 write-replay 元数据（§3.2.7）。

进程未显式 ``set_mcp_write_tool_meta_registry`` 时，``WasmRuntime`` 仍会与内置表合并，
避免 ``tool_meta is None`` 隐式「全放行」；未知工具名使用保守默认。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# 未知写工具：保守视为非确定性且要求幂等键，未提供键时由 evaluate_write_replay_policy 拒绝 program 侧 replay
DEFAULT_UNKNOWN_WRITE_TOOL_META: Dict[str, Any] = {
    "nondeterministic": True,
    "requires_idempotency_for_replay": True,
}

# Baseline / ToolPro 常见 Directus & MinIO & memos 写端点（与 exp2/baseline/directus_tools 名称对齐）
BUILTIN_MCP_WRITE_TOOL_META: Dict[str, Dict[str, Any]] = {
    # Directus 列表读：在 write_mode 下须与 patch 等写操作共存，不可落入「未知工具」保守策略，
    # 否则 evaluate_write_replay_policy 会误判为需幂等的非确定性端点并短路 get_items。
    "get_items": {
        "nondeterministic": False,
        "requires_idempotency_for_replay": False,
    },
    # MinIO / Memos 只读：与 get_items 相同，避免落入 UNKNOWN 被误判为需幂等的写端点
    "minio_list_objects": {
        "nondeterministic": False,
        "requires_idempotency_for_replay": False,
    },
    "minio_get_object": {
        "nondeterministic": False,
        "requires_idempotency_for_replay": False,
    },
    "memos_list_recent": {
        "nondeterministic": False,
        "requires_idempotency_for_replay": False,
    },
    "memos_get_memos": {
        "nondeterministic": False,
        "requires_idempotency_for_replay": False,
    },
    "patch_item": {
        "nondeterministic": False,
        "requires_idempotency_for_replay": False,
    },
    "post_items": {
        "nondeterministic": True,
        "requires_idempotency_for_replay": True,
    },
    "minio_upload_object": {
        "nondeterministic": True,
        "requires_idempotency_for_replay": True,
    },
    "minio_delete_object": {
        "nondeterministic": True,
        "requires_idempotency_for_replay": True,
    },
    "minio_move_object": {
        "nondeterministic": True,
        "requires_idempotency_for_replay": True,
    },
    "minio_copy_object": {
        "nondeterministic": True,
        "requires_idempotency_for_replay": True,
    },
    "prepare_bench_seed": {
        "nondeterministic": True,
        "requires_idempotency_for_replay": True,
    },
    "memos_create": {
        "nondeterministic": True,
        "requires_idempotency_for_replay": True,
    },
    "memos_delete": {
        "nondeterministic": True,
        "requires_idempotency_for_replay": True,
    },
}


def merge_write_tool_meta(
    tool_name: str,
    registry_overlay: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    base = dict(
        BUILTIN_MCP_WRITE_TOOL_META.get(tool_name, DEFAULT_UNKNOWN_WRITE_TOOL_META)
    )
    if isinstance(registry_overlay, dict):
        ov = registry_overlay.get(tool_name)
        if isinstance(ov, dict):
            base.update(ov)
    return base
