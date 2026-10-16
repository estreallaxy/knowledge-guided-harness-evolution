"""Shared utilities — JSON I/O and code sanitization."""

from __future__ import annotations

import ast
import json
import traceback
from collections.abc import Generator
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger
from pydantic_core import to_jsonable_python

if TYPE_CHECKING:
    from tree_sitter import Node


# ── JSON file I/O ────────────────────────────────────────────────────


def read_json_file(json_file: str, encoding="utf-8") -> Any:
    path = Path(json_file)
    if not path.exists():
        raise FileNotFoundError(f"json_file: {json_file} not found")
    with open(path, encoding=encoding) as f:
        return json.load(f)


def write_json_file(json_file: str, data: Any, encoding: str | None = None, indent: int = 4) -> None:
    folder = Path(json_file).parent
    folder.mkdir(parents=True, exist_ok=True)
    with open(json_file, "w", encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=indent, default=to_jsonable_python)


# ── Code sanitizer (tree-sitter based) ───────────────────────────────


class _NodeType(Enum):
    CLASS = "class_definition"
    FUNCTION = "function_definition"
    IMPORT = ["import_statement", "import_from_statement"]
    IDENTIFIER = "identifier"
    ATTRIBUTE = "attribute"
    RETURN = "return_statement"
    EXPRESSION = "expression_statement"
    ASSIGNMENT = "assignment"


def _traverse_tree(node: Node) -> Generator[Node, None, None]:
    cursor = node.walk()
    depth = 0
    visited_children = False
    while True:
        if not visited_children:
            yield cursor.node
            if not cursor.goto_first_child():
                depth += 1
                visited_children = True
        elif cursor.goto_next_sibling():
            visited_children = False
        elif not cursor.goto_parent() or depth == 0:
            break
        else:
            depth -= 1


def _syntax_check(code: str, verbose: bool = False) -> bool:
    try:
        ast.parse(code)
        return True
    except (SyntaxError, MemoryError):
        if verbose:
            traceback.print_exc()
        return False


def _code_extract(text: str) -> str:
    lines = text.split("\n")
    n = len(lines)
    if n == 0:
        return ""
    # Try full text first
    if _syntax_check(text):
        return text
    # Shrink from the end, then from the start — O(n) in the common case
    best = ""
    best_count = 0
    for start in range(n):
        for end in range(n, start, -1):
            candidate = "\n".join(lines[start:end])
            if _syntax_check(candidate):
                count = sum(1 for line in lines[start:end] if line.strip())
                if count > best_count:
                    best_count = count
                    best = candidate
                break  # found longest valid block from this start, move on
    return best


def _get_definition_name(node: Node) -> str | None:
    for child in node.children:
        if child.type == _NodeType.IDENTIFIER.value:
            return child.text.decode("utf8")


def _has_return_statement(node: Node) -> bool:
    for n in _traverse_tree(node):
        if n.type == _NodeType.RETURN.value:
            return True
    return False


def _get_deps(nodes: list[tuple[str, Node]]) -> dict[str, set[str]]:
    def dfs(node: Node, deps: set[str]) -> None:
        for child in node.children:
            if child.type == _NodeType.IDENTIFIER.value:
                deps.add(child.text.decode("utf8"))
            else:
                dfs(child, deps)

    name2deps: dict[str, set[str]] = {}
    for name, node in nodes:
        deps: set[str] = set()
        dfs(node, deps)
        name2deps[name] = deps
    return name2deps


def _get_function_dependency(entrypoint: str, call_graph: dict[str, set[str]]) -> set[str]:
    queue = [entrypoint]
    visited = {entrypoint}
    while queue:
        current = queue.pop(0)
        if current not in call_graph:
            continue
        for neighbour in call_graph[current]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return visited


def sanitize(code: str, entrypoint: str | None = None) -> str:
    """Sanitize and extract relevant parts of Python code.

    Falls back to returning the input code if tree-sitter is unavailable.
    """
    try:
        import tree_sitter_python
        from tree_sitter import Language, Parser

        code = _code_extract(code)
        code_bytes = bytes(code, "utf8")
        parser = Parser(Language(tree_sitter_python.language()))
        tree = parser.parse(code_bytes)

        class_names: set[str] = set()
        function_names: set[str] = set()
        variable_names: set[str] = set()
        root_node = tree.root_node
        import_nodes: list[Node] = []
        definition_nodes: list[tuple[str, Node]] = []

        for child in root_node.children:
            if child.type in _NodeType.IMPORT.value:
                import_nodes.append(child)
            elif child.type == _NodeType.CLASS.value:
                name = _get_definition_name(child)
                if name not in class_names | variable_names | function_names:
                    definition_nodes.append((name, child))
                    class_names.add(name)
            elif child.type == _NodeType.FUNCTION.value:
                name = _get_definition_name(child)
                if name not in function_names | variable_names | class_names and _has_return_statement(child):
                    definition_nodes.append((name, child))
                    function_names.add(name)
            elif child.type == _NodeType.EXPRESSION.value and child.children[0].type == _NodeType.ASSIGNMENT.value:
                subchild = child.children[0]
                name = _get_definition_name(subchild)
                if name not in variable_names | function_names | class_names:
                    definition_nodes.append((name, subchild))
                    variable_names.add(name)

        if entrypoint:
            name2deps = _get_deps(definition_nodes)
            reachable = _get_function_dependency(entrypoint, name2deps)
        else:
            reachable = None

        output = b""
        for node in import_nodes:
            output += code_bytes[node.start_byte : node.end_byte] + b"\n"
        for name, node in definition_nodes:
            if reachable is not None and name not in reachable:
                continue
            output += code_bytes[node.start_byte : node.end_byte] + b"\n"

        return output[:-1].decode("utf8") if output else code
    except Exception as e:
        logger.warning(f"sanitize failed, returning code unchanged: {e}")
        return str(code)
