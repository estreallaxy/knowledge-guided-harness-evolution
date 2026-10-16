"""Tools available to ReAct operators: a safe math evaluator and a sandboxed code executor."""

from __future__ import annotations

import ast
import asyncio
import functools
import math
import operator
import os
import subprocess
import sys
import tempfile
from typing import Any

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_ALLOWED_NAMES: dict[str, Any] = {
    "pi": math.pi,
    "tau": math.tau,
    "e": math.e,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "pow": pow,
    "sqrt": math.sqrt,
    "cbrt": lambda x: math.copysign(abs(x) ** (1.0 / 3.0), x),
    "floor": math.floor,
    "ceil": math.ceil,
    "trunc": math.trunc,
    "copysign": math.copysign,
    "fabs": math.fabs,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "radians": math.radians,
    "degrees": math.degrees,
    "hypot": math.hypot,
    "gcd": math.gcd,
    "lcm": math.lcm,
    "factorial": math.factorial,
    "comb": math.comb,
    "perm": math.perm,
}


class _SafeEval(ast.NodeVisitor):
    def visit_BinOp(self, node: ast.BinOp) -> Any:
        return _ALLOWED_OPERATORS[type(node.op)](self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        return _ALLOWED_OPERATORS[type(node.op)](self.visit(node.operand))

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Constant of type {type(node.value).__name__} not allowed")

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[node.id]
        raise ValueError(f"Name '{node.id}' not allowed")

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_NAMES:
            raise ValueError("Function not allowed")
        return _ALLOWED_NAMES[node.func.id](*[self.visit(arg) for arg in node.args])

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Operation {type(node).__name__} not allowed")


class MathCalculatorTool:
    async def calculate(self, expression: str) -> dict[str, Any]:
        try:
            tree = ast.parse(expression, mode="eval")
            result = _SafeEval().visit(tree.body)
            return {"success": True, "result": result, "expression": expression}
        except Exception as e:
            return {"success": False, "error": str(e), "expression": expression}


class CodeExecutionTool:
    TIMEOUT_SEC = 60

    async def execute(self, code: str) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name
        try:
            result = await asyncio.to_thread(
                functools.partial(
                    subprocess.run,
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.TIMEOUT_SEC,
                )
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "code": code,
                "raw_content": result.stdout,
                "content": result.stdout,
                "output": result.stdout,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "code": code, "raw_content": "", "stdout": "", "stderr": ""}
        finally:
            try:
                os.unlink(temp_file)
            except OSError:
                pass


_TOOL_CLASSES: dict[str, type] = {
    "math_calculator": MathCalculatorTool,
    "code_executor": CodeExecutionTool,
}


def get_tool_object(tool_name: str) -> type | None:
    return _TOOL_CLASSES.get(tool_name)
