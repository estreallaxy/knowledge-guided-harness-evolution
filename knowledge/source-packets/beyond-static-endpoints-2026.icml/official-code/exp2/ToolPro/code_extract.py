"""从模型输出中提取围栏代码。"""

from __future__ import annotations


def extract_code_from_response(response: str, language: str) -> str:
    """
    language: rust | go | lua
    优先匹配对应语言的围栏；否则第一个通用 ``` 块；再否则全文。
    """
    preferred_opens = {
        "rust": ("```rust",),
        "go": ("```go", "```golang"),
        "lua": ("```lua",),
    }
    opens = preferred_opens.get(language, ("```",))

    lines = response.split("\n")
    code_lines: list[str] = []
    in_block = False

    for line in lines:
        stripped = line.strip()
        if not in_block:
            if any(stripped.startswith(o) for o in opens):
                in_block = True
            continue
        if stripped.startswith("```"):
            break
        code_lines.append(line)

    if code_lines:
        return "\n".join(code_lines).strip()

    in_block = False
    code_lines = []
    for line in lines:
        if line.strip().startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            code_lines.append(line)
    if code_lines:
        return "\n".join(code_lines).strip()

    return response.strip()
