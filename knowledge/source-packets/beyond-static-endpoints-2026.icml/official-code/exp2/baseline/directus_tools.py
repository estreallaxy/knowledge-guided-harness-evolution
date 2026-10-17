"""
Directus Items 端点工具封装（与 exp2/init_directus_forms.py 默认连接信息一致，写死在下方常量）。
对应 REST：GET /items/{collection}、PATCH /items/{collection}/{id}、POST /items/{collection}
说明参考：exp2/api_calls_list.txt 与 Directus Query Parameters。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

from exp2.exp_case4.config import load_case4_config
from exp2.exp_case4.memos_client import MemosClient
from exp2.exp_case4.seed_data import ensure_seed_files
from exp2.exp_case4.storage_client import MinioStorageClient

# 与 exp2/init_directus_forms.py 中默认环境变量 / 默认令牌一致（写死，不读环境变量）
DIRECTUS_BASE_URL = "http://localhost:8055"
DIRECTUS_ADMIN_EMAIL = "admin@example.com"
DIRECTUS_ADMIN_PASSWORD = "admin123"
DIRECTUS_ACCESS_TOKEN = "qsCquMhF22d3MRS7BT_3N0RNER65QK1_"

Json = Dict[str, Any]

# 与 init_directus_forms 写入时一致：orders / exchange_logs 中「类列表」字段用 JSON 数组提交
_ITEMS_LIKE_KEYS = frozenset({"items", "old_items", "new_items"})


def coerce_items_like_field(value: Any) -> List[str]:
    """
    将 Agent 可能传入的多种形式统一为字符串列表，供 PATCH/POST 序列化为 JSON 数组
    （与 init_directus_forms.create_items 使用 list 写入的行为一致）。
    """
    if value is None:
        return []
    if isinstance(value, list):
        out: List[str] = []
        for x in value:
            if x is None:
                continue
            s = str(x).strip()
            if s:
                out.append(s)
        return out
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [str(value)]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [
                        str(x).strip()
                        for x in parsed
                        if x is not None and str(x).strip() != ""
                    ]
                return [str(parsed).strip()] if str(parsed).strip() else []
            except json.JSONDecodeError:
                pass
        return [s]
    s = str(value).strip()
    return [s] if s else []


def _rename_dict_keys_recursive(obj: Any, old_key: str, new_key: str) -> Any:
    """在嵌套 dict/list 中将键 old_key 重命名为 new_key（仅键名，不改值）。"""
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            nk = new_key if k == old_key else k
            out[nk] = _rename_dict_keys_recursive(v, old_key, new_key)
        return out
    if isinstance(obj, list):
        return [_rename_dict_keys_recursive(x, old_key, new_key) for x in obj]
    return obj


def normalize_write_fields(data: Json) -> Json:
    """规范化单次写入的 data/记录：items 类字段 → list[str]；total → float（若可转换）。"""
    if not data:
        return {}
    out = dict(data)
    # 常见模型误用：订单总价字段为 total（与 init_directus_forms / 期望 JSON 一致），非 total_amount。
    if "total_amount" in out:
        if "total" not in out:
            out["total"] = out.pop("total_amount")
        else:
            out.pop("total_amount", None)
    for key in _ITEMS_LIKE_KEYS:
        if key in out:
            out[key] = coerce_items_like_field(out[key])
    if "total" in out:
        tv = out["total"]
        if tv is not None:
            try:
                out["total"] = float(tv)
            except (TypeError, ValueError):
                pass
    return out


# 供 System Prompt 使用的工具说明书（文本）
TOOL_LIST_DOC = """
【MCP 已注册工具与后端端点对应关系】
每次 tool_call 的 "tool" 字段须与下列名称完全一致（区分大小写）。

────────────────────────────────────────
工具名：get_items
对应 HTTP：GET /items/{collection}
用途：列出指定集合中的条目，支持过滤、排序、字段筛选、分页等（与 Directus 全局 Query Parameters 一致）。

输入参数（arguments 对象）：
  • collection（string，必填）
      集合标识。本实验中可能出现的取值示例：customers、orders、exchange_logs。
  • query（object，可选）
      查询条件对象。键名与 Directus 文档中的查询参数一致，常用键包括：
      - filter：嵌套对象，表示字段条件（将展开为 filter[字段][操作符]=值 形式的查询串）。
        customers 集合的邮编字段名为 zip_code（若误写 postal_code，本工具在 collection=customers 时会规范为 zip_code）。
      - fields：字符串，逗号分隔字段名，或按 Directus 约定传递。
      - sort：排序字段，如 "id" 或 "-date_created"。
      - limit：数量上限；整数。若省略，本工具默认使用 -1（尽量取全量）。
      - offset、meta 等：按 Directus 文档使用。
      若省略 sort，本工具默认 sort=id。

返回约定：
  JSON 对象，至少含 status_code（整数）；若响应体可解析为 JSON 则置于 body；否则可能含 text_preview 片段。
  列表类成功响应中，记录数组常见位于 body.data。
  为减轻读到 HTTP/中间层缓存陈旧数据的概率，本工具在 GET 上附带 Cache-Control: no-cache（与 Baseline 验证器拉取实况时一致）。

────────────────────────────────────────
工具名：patch_item
对应 HTTP：PATCH /items/{collection}/{item_id}
用途：按主键更新单条条目的部分字段（部分更新）。

输入参数（arguments 对象）：
  • collection（string，必填）集合标识。
  • item_id（integer 或 string，必填）该条目的主键 id。若为数字字符串，将按整数处理。
  • data（object，必填）
      要合并写入的字段键值对。本工具会将其规范后作为 PATCH 请求的 JSON 根对象发出（Directus 单条更新约定：顶层即字段，勿自行再包 "data"）。
      对 items / old_items / new_items：无论你传入 JSON 数组、JSON 数组字符串（含转义）、或单个 SKU 字符串，
      工具层会规范为与 init 脚本 POST 一致的「JSON 数组」再写入，避免 text 字段上双重编码导致 PATCH 不生效。
      订单总价字段须为 total（若误写 total_amount，工具层会映射为 total）。

返回约定：同 get_items（status_code、body 等）。

────────────────────────────────────────
工具名：post_items
对应 HTTP：POST /items/{collection}
用途：在指定集合中新建一条或多条条目。

输入参数（arguments 对象）：
  • collection（string，必填）集合标识。
  • records（array，必填）
      由若干「记录对象」组成的数组；每个对象对应一条待创建记录。若业务上只创建一条，仍须使用长度为 1 的数组。
      （与 init_directus_forms 批量写入时请求体为数组的用法一致。）

返回约定：同 get_items（status_code、body 等；创建成功时 body.data 常为新建记录或记录数组）。
────────────────────────────────────────
工具名：prepare_bench_seed
用途：在本地 bench_seed 目录生成 Case4 的 5 个固定文档。
输入参数：无。
返回约定：status_code=200，body.files 为文件名数组，body.dir 为目录路径。

────────────────────────────────────────
工具名：minio_upload_object
用途：上传文本对象到 MinIO。
输入参数：
  • object_name（string，必填）对象键名，例如 incoming/invoice_paid_1.txt
  • content（string，可选）文本内容；若省略、为空串或仅空白，则按 object_name 末尾文件名从 bench_seed 读取（与省略行为一致）。

工具名：minio_list_objects
用途：列出某前缀下对象。
输入参数：
  • prefix（string，必填）例如 incoming/

工具名：minio_get_object
用途：下载对象文本。
输入参数：
  • object_name（string，必填）

工具名：minio_copy_object
用途：复制对象。
输入参数：
  • source_key（string，必填）
  • target_key（string，必填）

工具名：minio_move_object
用途：移动对象（copy + delete）。
输入参数：
  • source_key（string，必填）
  • target_key（string，必填）

工具名：minio_delete_object
用途：删除对象。
输入参数：
  • object_name（string，必填）

────────────────────────────────────────
工具名：memos_create
用途：创建一条 memo。
输入参数：
  • title（string，必填）
  • content（string，必填）
  • visibility（string，可选，默认 PRIVATE）

工具名：memos_list_recent
用途：查询 memo 列表并按标题过滤。
输入参数：
  • title_contains（string，可选，默认空）
  • limit（integer，可选，默认 20）

工具名：memos_delete
用途：删除 memo。
输入参数：
  • memo_name（string，必填；可为 name 或 id）
────────────────────────────────────────
""".strip()


def _flatten_query(obj: Any, parent_key: str = "") -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = f"{parent_key}[{k}]" if parent_key else str(k)
            pairs.extend(_flatten_query(v, nk))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            nk = f"{parent_key}[{i}]"
            pairs.extend(_flatten_query(item, nk))
    else:
        if not parent_key:
            return pairs
        if isinstance(obj, bool):
            s = "true" if obj else "false"
        else:
            s = str(obj)
        pairs.append((parent_key, s))
    return pairs


def _merge_query_params(query: Json) -> Dict[str, str]:
    return {k: v for k, v in _flatten_query(query)}


def _coerce_item_id(raw: Any) -> Any:
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw
    if isinstance(raw, str) and raw.strip().lstrip("-").isdigit():
        return int(raw.strip())
    return raw


class DirectusToolRunner:
    """
    使用写死的 DIRECTUS_* 常量建立会话并执行三项 Items 工具。
    调用方须在用完後调用 close()。
    """

    def __init__(self) -> None:
        self._http = httpx.Client(
            base_url=DIRECTUS_BASE_URL.rstrip("/"),
            timeout=30.0,
            trust_env=False,
        )
        token = (DIRECTUS_ACCESS_TOKEN or "").strip()
        if token:
            self._token: Optional[str] = token
        else:
            self._token = None
            self._login_with_password()
        self._case4_storage: Optional[MinioStorageClient] = None
        self._case4_memos: Optional[MemosClient] = None
        self._case4_seed_dir = Path(__file__).resolve().parents[1] / "exp_case4" / "bench_seed"

    def _login_with_password(self) -> None:
        resp = self._http.post(
            "/auth/login",
            json={
                "email": DIRECTUS_ADMIN_EMAIL,
                "password": DIRECTUS_ADMIN_PASSWORD,
            },
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Directus 登录失败: {resp.status_code} {resp.text[:500]}"
            )
        data = resp.json().get("data", {})
        tok = data.get("access_token")
        if not tok:
            raise RuntimeError("Directus 登录成功但未返回 access_token")
        self._token = tok

    def _headers(self) -> Dict[str, str]:
        h: Dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        headers = {**self._headers(), **kwargs.pop("headers", {})}
        return self._http.request(method, path, headers=headers, **kwargs)

    def close(self) -> None:
        self._http.close()
        if self._case4_memos is not None:
            self._case4_memos.close()

    def _response_payload(self, resp: Any) -> Json:
        out: Json = {"status_code": resp.status_code}
        try:
            if resp.content:
                out["body"] = resp.json()
            else:
                out["body"] = None
        except Exception:
            out["body"] = None
            out["text_preview"] = (resp.text or "")[:4000]
        return out

    def call(self, tool: str, arguments: Optional[Json]) -> str:
        args = arguments or {}
        try:
            if tool == "get_items":
                return json.dumps(
                    self._get_items(
                        str(args.get("collection", "")),
                        args.get("query"),
                    ),
                    ensure_ascii=False,
                )
            if tool == "patch_item":
                return json.dumps(
                    self._patch_item(
                        str(args.get("collection", "")),
                        args.get("item_id"),
                        args.get("data") if isinstance(args.get("data"), dict) else {},
                    ),
                    ensure_ascii=False,
                )
            if tool == "post_items":
                return json.dumps(
                    self._post_items(
                        str(args.get("collection", "")),
                        args.get("records"),
                    ),
                    ensure_ascii=False,
                )
            if tool == "prepare_bench_seed":
                return json.dumps(self._prepare_bench_seed(), ensure_ascii=False)
            if tool == "minio_upload_object":
                return json.dumps(
                    self._minio_upload_object(
                        str(args.get("object_name", "")),
                        args.get("content"),
                    ),
                    ensure_ascii=False,
                )
            if tool == "minio_list_objects":
                return json.dumps(
                    self._minio_list_objects(str(args.get("prefix", ""))),
                    ensure_ascii=False,
                )
            if tool == "minio_get_object":
                return json.dumps(
                    self._minio_get_object(str(args.get("object_name", ""))),
                    ensure_ascii=False,
                )
            if tool == "minio_copy_object":
                return json.dumps(
                    self._minio_copy_object(
                        str(args.get("source_key", "")),
                        str(args.get("target_key", "")),
                    ),
                    ensure_ascii=False,
                )
            if tool == "minio_move_object":
                return json.dumps(
                    self._minio_move_object(
                        str(args.get("source_key", "")),
                        str(args.get("target_key", "")),
                    ),
                    ensure_ascii=False,
                )
            if tool == "minio_delete_object":
                return json.dumps(
                    self._minio_delete_object(str(args.get("object_name", ""))),
                    ensure_ascii=False,
                )
            if tool == "memos_create":
                return json.dumps(
                    self._memos_create(
                        str(args.get("title", "")),
                        str(args.get("content", "")),
                        str(args.get("visibility", "PRIVATE") or "PRIVATE"),
                    ),
                    ensure_ascii=False,
                )
            if tool == "memos_list_recent":
                return json.dumps(
                    self._memos_list_recent(
                        str(args.get("title_contains", "")),
                        int(args.get("limit", 20) or 20),
                    ),
                    ensure_ascii=False,
                )
            if tool == "memos_delete":
                return json.dumps(
                    self._memos_delete(str(args.get("memo_name", ""))),
                    ensure_ascii=False,
                )
        except Exception as e:
            return json.dumps(
                {"error": str(e), "tool": tool, "arguments": args},
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "error": "unknown_tool",
                "tool": tool,
                "message": "未知工具名；请使用工具说明书中的名称",
            },
            ensure_ascii=False,
        )

    def _get_items(
        self, collection: str, query: Optional[Any]
    ) -> Json:
        if not collection:
            return {"error": "collection 不能为空"}
        q: Json = {}
        if isinstance(query, dict):
            q.update(query)
        # customers 集合 schema 使用 zip_code；模型常误写 postal_code，在此对齐以免过滤恒为空。
        if collection.strip().lower() == "customers":
            q = _rename_dict_keys_recursive(q, "postal_code", "zip_code")
        if "limit" not in q:
            q["limit"] = -1
        if "sort" not in q:
            q["sort"] = "id"
        params = _merge_query_params(q)
        resp = self._request(
            "GET",
            f"/items/{collection}",
            params=params,
            headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
        )
        return self._response_payload(resp)

    def _patch_item(
        self, collection: str, item_id: Any, data: Json
    ) -> Json:
        if not collection:
            return {"error": "collection 不能为空"}
        if item_id is None:
            return {"error": "item_id 不能为空"}
        iid = _coerce_item_id(item_id)
        payload = normalize_write_fields(data)
        # Directus REST「Update an item」：请求体为字段对象本身，勿再包一层 "data"
        # （包成 {"data": {...}} 时部分版本会忽略真实字段更新，表现为 200 但库内未变）
        resp = self._request(
            "PATCH",
            f"/items/{collection}/{iid}",
            json=payload,
        )
        return self._response_payload(resp)

    def _post_items(self, collection: str, records: Any) -> Json:
        if not collection:
            return {"error": "collection 不能为空"}
        if records is None:
            return {"error": "records 不能为空，须为非空对象数组"}
        if isinstance(records, dict):
            payload = [records]
        elif isinstance(records, list):
            if len(records) == 0:
                return {"error": "records 须至少包含一条记录"}
            payload = records
        else:
            return {"error": "records 须为对象或对象数组"}
        norm_payload: List[Any] = []
        for rec in payload:
            if isinstance(rec, dict):
                norm_payload.append(normalize_write_fields(rec))
            else:
                norm_payload.append(rec)
        resp = self._request("POST", f"/items/{collection}", json=norm_payload)
        return self._response_payload(resp)

    def _ensure_case4_clients(self) -> None:
        if self._case4_storage is not None and self._case4_memos is not None:
            return
        cfg = load_case4_config()
        self._case4_storage = MinioStorageClient(cfg.minio)
        self._case4_memos = MemosClient(cfg.memos)

    def _prepare_bench_seed(self) -> Json:
        files = ensure_seed_files(self._case4_seed_dir)
        return {
            "status_code": 200,
            "body": {
                "dir": str(self._case4_seed_dir),
                "files": sorted(files.keys()),
            },
        }

    def _seed_content_by_object(self, object_name: str) -> str:
        fname = object_name.rsplit("/", 1)[-1]
        p = self._case4_seed_dir / fname
        if not p.is_file():
            ensure_seed_files(self._case4_seed_dir)
        if not p.is_file():
            raise FileNotFoundError(f"bench_seed 不存在文件: {fname}")
        return p.read_text(encoding="utf-8")

    def _minio_upload_object(self, object_name: str, content: Any) -> Json:
        if not object_name:
            return {"error": "object_name 不能为空"}
        self._ensure_case4_clients()
        # None 时沿用 bench_seed；空串/纯空白与 None 等价，避免 Guest 传 content:"" 仍 200 导致对象无正文、Case4 校验失败
        use_seed = False
        if content is None:
            use_seed = True
        elif isinstance(content, (bytes, bytearray)):
            if len(content) == 0:
                use_seed = True
        elif isinstance(content, str):
            if not content.strip():
                use_seed = True
        if use_seed:
            try:
                text = self._seed_content_by_object(object_name)
            except FileNotFoundError as e:
                return {
                    "error": (
                        f"{e}; 请提供非空 content，或 object_name 末尾文件名须与 bench_seed 中已有文件一致"
                    )
                }
        else:
            text = (
                content.decode("utf-8", errors="replace")
                if isinstance(content, (bytes, bytearray))
                else str(content)
            )
        self._case4_storage.upload_text(object_name, text)
        return {"status_code": 200, "body": {"object_name": object_name, "uploaded": True}}

    def _minio_list_objects(self, prefix: str) -> Json:
        if not prefix:
            return {"error": "prefix 不能为空"}
        self._ensure_case4_clients()
        objs = self._case4_storage.list_objects(prefix)
        return {"status_code": 200, "body": {"objects": objs, "count": len(objs)}}

    def _minio_get_object(self, object_name: str) -> Json:
        if not object_name:
            return {"error": "object_name 不能为空"}
        self._ensure_case4_clients()
        text = self._case4_storage.get_text(object_name)
        return {"status_code": 200, "body": {"object_name": object_name, "content": text}}

    def _minio_copy_object(self, source_key: str, target_key: str) -> Json:
        if not source_key or not target_key:
            return {"error": "source_key/target_key 不能为空"}
        self._ensure_case4_clients()
        self._case4_storage.copy_object(source_key, target_key)
        return {"status_code": 200, "body": {"source_key": source_key, "target_key": target_key}}

    def _minio_move_object(self, source_key: str, target_key: str) -> Json:
        if not source_key or not target_key:
            return {"error": "source_key/target_key 不能为空"}
        self._ensure_case4_clients()
        self._case4_storage.move_object(source_key, target_key)
        return {"status_code": 200, "body": {"source_key": source_key, "target_key": target_key}}

    def _minio_delete_object(self, object_name: str) -> Json:
        if not object_name:
            return {"error": "object_name 不能为空"}
        self._ensure_case4_clients()
        self._case4_storage.delete_object(object_name)
        return {"status_code": 200, "body": {"object_name": object_name, "deleted": True}}

    def _memos_create(self, title: str, content: str, visibility: str) -> Json:
        if not title:
            return {"error": "title 不能为空"}
        self._ensure_case4_clients()
        memo_id, final_title = self._case4_memos.create_followup_memo(
            filename=title.replace("[FOLLOWUP] ", "").strip() or title,
            content=content,
        ) if title.startswith("[FOLLOWUP] ") else self._create_generic_memo(title, content, visibility)
        return {"status_code": 200, "body": {"memo_name": memo_id, "title": final_title}}

    def _create_generic_memo(self, title: str, content: str, visibility: str) -> Tuple[str, str]:
        # create_followup_memo 带固定标题规则；通用标题走底层 POST。
        payload = {"title": title, "content": content, "visibility": visibility or "PRIVATE"}
        url = f"{self._case4_memos.base_api}/memos"
        resp = self._case4_memos.http.post(url, json=payload)
        self._case4_memos._record(
            len(url.encode("utf-8")) + len(str(payload).encode("utf-8")),
            len(resp.text.encode("utf-8")),
        )
        resp.raise_for_status()
        body = resp.json()
        memo = body.get("memo") or body.get("data") or body
        memo_name = str(memo.get("name") or memo.get("id") or "")
        return memo_name or title, title

    def _memos_list_recent(self, title_contains: str, limit: int) -> Json:
        self._ensure_case4_clients()
        memos = self._case4_memos.list_memos(page_size=max(1, limit))
        if title_contains:

            def _memo_match_text(m: dict) -> str:
                prop = m.get("property") if isinstance(m.get("property"), dict) else {}
                return str(
                    m.get("title")
                    or prop.get("title")
                    or m.get("content")
                    or ""
                )

            memos = [m for m in memos if title_contains in _memo_match_text(m)]
        memos = memos[: max(1, limit)]
        return {"status_code": 200, "body": {"count": len(memos), "data": memos}}

    def _memos_delete(self, memo_name: str) -> Json:
        if not memo_name:
            return {"error": "memo_name 不能为空"}
        self._ensure_case4_clients()
        self._case4_memos.delete_memo(memo_name)
        return {"status_code": 200, "body": {"memo_name": memo_name, "deleted": True}}
