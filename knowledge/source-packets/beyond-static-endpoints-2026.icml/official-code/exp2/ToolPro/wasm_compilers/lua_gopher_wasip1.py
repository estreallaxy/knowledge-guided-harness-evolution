"""
Lua → WASM（WASI）：将用户 Lua 以 Base64 形式嵌入纯 Go 工程，通过 yuin/gopher-lua 在 main 中加载执行；
与 CompilationEngine 相同采用「临时目录 + 子进程 go build」。

- 先在宿主目标上 `go run .`：运行期执行 DoString，语法/加载错误会失败（对齐「可执行语义」门闸）。
- 再 GOOS=wasip1 GOARCH=wasm go build 产出 wasm。
"""

from __future__ import annotations

import base64
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

_GOPHER_LUA = "github.com/yuin/gopher-lua"
_GOPHER_VER = "v1.1.1"

_SHIM_TEMPLATE = """package main

import (
	"encoding/base64"
	"fmt"

	lua "github.com/yuin/gopher-lua"
)

const _toolProLuaScriptB64 = "{b64}"

func main() {{
	raw, err := base64.StdEncoding.DecodeString(_toolProLuaScriptB64)
	if err != nil {{
		panic(err)
	}}
	L := lua.NewState()
	defer L.Close()
	if err := L.DoString(string(raw)); err != nil {{
		panic(fmt.Sprintf("toolpro lua: %%v", err))
	}}
}}
"""


def compile_lua_via_gopher_wasip1(source_code: str) -> Dict[str, Any]:
    go = shutil.which("go")
    if not go:
        return {
            "success": False,
            "error": "未找到 go（Lua→WASM  shim 依赖 Go 1.21+）",
            "wasm_bytes": None,
            "cached": False,
            "template_hit": False,
            "backend": "lua_gopher_wasip1",
        }

    script = source_code.strip()
    if not script:
        return {
            "success": False,
            "error": "Lua 源码为空",
            "wasm_bytes": None,
            "cached": False,
            "template_hit": False,
            "backend": "lua_gopher_wasip1",
        }

    b64 = base64.standard_b64encode(script.encode("utf-8")).decode("ascii")
    main_go = _SHIM_TEMPLATE.format(b64=b64)

    env_wasip1 = os.environ.copy()
    env_wasip1["GOOS"] = "wasip1"
    env_wasip1["GOARCH"] = "wasm"
    env_wasip1["CGO_ENABLED"] = "0"

    try:
        with tempfile.TemporaryDirectory(prefix="toolpro_lua_") as tmp:
            root = Path(tmp)
            (root / "main.go").write_text(main_go, encoding="utf-8")
            mod = f"""module toolpro_lua_staging

go 1.21

require {_GOPHER_LUA} {_GOPHER_VER}
"""
            (root / "go.mod").write_text(mod, encoding="utf-8")

            pr = subprocess.run(
                [go, "mod", "tidy"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=300,
                env=os.environ.copy(),
            )
            if pr.returncode != 0:
                err = (pr.stderr or "") + (pr.stdout or "")
                return {
                    "success": False,
                    "error": f"go mod tidy 失败:\n{err[-8000:]}",
                    "wasm_bytes": None,
                    "cached": False,
                    "template_hit": False,
                    "backend": "lua_gopher_wasip1",
                }

            # 宿主上执行一次：验证 Lua 可被 gopher-lua 加载（对齐第一层「可运行」语义）
            pr_run = subprocess.run(
                [go, "run", "."],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if pr_run.returncode != 0:
                err = (pr_run.stderr or "") + (pr_run.stdout or "")
                return {
                    "success": False,
                    "error": f"go run（Lua 加载/执行）失败:\n{err[-8000:]}",
                    "wasm_bytes": None,
                    "cached": False,
                    "template_hit": False,
                    "backend": "lua_gopher_wasip1",
                }

            out_wasm = root / "toolpro_lua_out.wasm"
            pr_b = subprocess.run(
                [go, "build", "-o", str(out_wasm), "."],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=300,
                env=env_wasip1,
            )
            if pr_b.returncode != 0:
                err = (pr_b.stderr or "") + (pr_b.stdout or "")
                return {
                    "success": False,
                    "error": f"go build wasip1/wasm（Lua shim）失败:\n{err[-8000:]}",
                    "wasm_bytes": None,
                    "cached": False,
                    "template_hit": False,
                    "backend": "lua_gopher_wasip1",
                }

            data = out_wasm.read_bytes()
            return {
                "success": True,
                "wasm_bytes": data,
                "error": None,
                "cached": False,
                "template_hit": False,
                "backend": "lua_gopher_wasip1",
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Lua WASI 编译或 go run 超时",
            "wasm_bytes": None,
            "cached": False,
            "template_hit": False,
            "backend": "lua_gopher_wasip1",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Lua gopher-lua WASI 异常: {e}",
            "wasm_bytes": None,
            "cached": False,
            "template_hit": False,
            "backend": "lua_gopher_wasip1",
        }
