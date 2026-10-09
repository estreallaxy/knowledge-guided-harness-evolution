#!/usr/bin/env python3
"""Agent-Computer Interface toolkit: windowed viewer, guardrailed editor, feedback.

Mechanism source: SWE-agent, "Agent-Computer Interfaces Enable Automated
Software Engineering" (arXiv:2405.15793, NeurIPS 2024).

This is a harness-agnostic skeleton of the mechanism:
- The viewer shows fixed-size windows with line numbers and supports search;
- Edits are checked after the write and rolled back on failure;
- Feedback formatting marks empty-but-successful results explicitly;
- Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import ast
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

DEFAULT_WINDOW = 100

# Syntax checker protocol: (source text, file path) -> error message ("" means ok).
SyntaxChecker = Callable[[str, str], str]


def python_syntax_checker(source: str, path: str) -> str:
    """Default checker: parse Python source; return "" when valid."""
    try:
        ast.parse(source)
    except SyntaxError as error:
        return f"{error.__class__.__name__} at line {error.lineno}: {error.msg}"
    return ""


@dataclass
class ViewWindow:
    """One window of a file: line-numbered excerpt plus scroll/size metadata."""

    path: str
    start: int  # 1-based first line of the window
    end: int  # 1-based last line of the window
    total: int  # total lines in the file
    lines: list[str]

    def render(self) -> str:
        numbered = [
            f"{self.start + offset:>5} {line}"
            for offset, line in enumerate(self.lines)
        ]
        header = f"[{self.path}] lines {self.start}-{self.end} of {self.total}"
        return "\n".join([header, *numbered])


class WindowedViewer:
    """View files through fixed-size windows instead of dumping whole files."""

    def __init__(self, window: int = DEFAULT_WINDOW):
        self.window = window

    def view(self, path: str, start: int = 1) -> ViewWindow:
        all_lines = Path(path).read_text(encoding="utf-8").splitlines()
        total = len(all_lines)
        start = max(1, min(start, max(total, 1)))
        end = min(total, start + self.window - 1)
        return ViewWindow(
            path=str(path),
            start=start,
            end=end,
            total=total,
            lines=all_lines[start - 1 : end],
        )

    def scroll(self, window: ViewWindow, offset: int) -> ViewWindow:
        """Scroll a window up/down by offset lines."""
        return self.view(window.path, start=window.start + offset)

    def search(self, path: str, pattern: str) -> list[tuple[int, str]]:
        """Return (line number, stripped line) for lines containing pattern."""
        matches = []
        for number, line in enumerate(
            Path(path).read_text(encoding="utf-8").splitlines(), start=1
        ):
            if pattern in line:
                matches.append((number, line.strip()))
        return matches


@dataclass
class EditResult:
    """Outcome of a guardrailed edit."""

    ok: bool
    rolled_back: bool
    message: str


class GuardrailedEditor:
    """Range-edit files, checking syntax after the write and rolling back on failure."""

    def __init__(self, checker: SyntaxChecker | None = None):
        self.checker = checker or python_syntax_checker

    def edit(self, path: str, start: int, end: int, replacement: str) -> EditResult:
        path_obj = Path(path)
        original = path_obj.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        if not (1 <= start <= end <= len(lines)):
            return EditResult(
                False,
                False,
                f"Range {start}-{end} is outside the file ({len(lines)} lines).",
            )
        replacement_lines = [line + "\n" for line in replacement.splitlines()]
        updated = "".join(lines[: start - 1] + replacement_lines + lines[end:])
        if not updated.endswith("\n"):
            updated += "\n"

        path_obj.write_text(updated, encoding="utf-8")
        error = self.checker(updated, str(path_obj))
        if error:
            path_obj.write_text(original, encoding="utf-8")
            return EditResult(False, True, f"Edit reverted: {error}")
        return EditResult(True, False, f"Edited {path_obj} lines {start}-{end}.")


def format_feedback(exit_code: int | None, output: str) -> str:
    """Feedback formatting: make empty-but-successful results explicit."""
    if exit_code is None:
        return "Command did not report an exit code; treat the state as unknown."
    if exit_code == 0:
        if output.strip():
            return output.rstrip()
        return "Your command ran successfully and did not produce any output."
    return f"Command failed with exit code {exit_code}.\n{output.rstrip()}"


DEMO_SOURCE = """\
def add(a, b):
    return a + b


def multiply(a, b):
    return a * b
"""


def demo_command(args: argparse.Namespace) -> None:
    """Minimal demo: windowed view, search, a valid edit, and a reverted bad edit."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "scratch.py"
        path.write_text(DEMO_SOURCE, encoding="utf-8")

        viewer = WindowedViewer(window=3)
        window = viewer.view(str(path))
        print("--- Windowed view ---")
        print(window.render())
        print("--- Scrolled view (+2) ---")
        print(viewer.scroll(window, offset=2).render())
        print("--- Search 'def' ---")
        for number, line in viewer.search(str(path), "def"):
            print(f"  {number}: {line}")

        editor = GuardrailedEditor()
        print("--- Valid edit (line 2) ---")
        print(editor.edit(str(path), 2, 2, "    return a + b  # checked").message)

        print("--- Invalid edit (syntax error, rolled back) ---")
        print(editor.edit(str(path), 2, 2, "    return a +").message)
        print("Line 2 after rollback:", path.read_text(encoding="utf-8").splitlines()[1])

        print("--- Feedback formatting ---")
        print(format_feedback(0, ""))
        print(format_feedback(1, "No such file or directory"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Windowed file viewing, guardrailed editing, and feedback formatting."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser(
        "demo", help="Exercise the viewer, the guardrailed editor, and feedback formatting"
    )
    demo.set_defaults(handler=demo_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
