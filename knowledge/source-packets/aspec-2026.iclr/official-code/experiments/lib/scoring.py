"""Per-dataset answer extraction and scoring functions."""

from __future__ import annotations

import re
import threading
from typing import Any, Callable, Dict, Optional, Tuple

import regex as _regex
from loguru import logger
from sympy import N, simplify
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr

from aspec.utils import sanitize

# ---------------------------------------------------------------------------
# MATH scoring
# ---------------------------------------------------------------------------


def extract_model_answer_math(text: str) -> str:
    """Extract answer from model output for MATH dataset."""
    from experiments.lib.eval_utils import _extract_string_from_output

    if not isinstance(text, str):
        text = _extract_string_from_output(text)

    # First try XML tags
    tag_patterns = [
        r"<final_answer>\s*([\s\S]*?)\s*</final_answer>",
        r"<answer>\s*([\s\S]*?)\s*</answer>",
        r"<refined>\s*([\s\S]*?)\s*</refined>",
        r"<refined_answer>\s*([\s\S]*?)\s*</refined_answer>",
    ]
    for p in tag_patterns:
        m = re.findall(p, text, re.IGNORECASE)
        if m:
            candidate = m[-1].strip()
            candidate = re.sub(r"^```[a-zA-Z]*\n|```$", "", candidate).strip().strip("`")
            if candidate:
                return candidate

    # Then try \boxed{} patterns (most common for MATH)
    pattern = r"\\boxed{((?:[^{}]|{[^{}]*})*)}"
    boxed_matches = re.findall(pattern, text, re.DOTALL)
    if boxed_matches:
        return boxed_matches[-1].strip()

    # Fallback to last sentence
    sentence_end_pattern = r"(?<!\d)[.!?]\s+"
    sentences = re.split(sentence_end_pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences[-1] if sentences else ""


def _is_digit(num: Any) -> bool:
    return _parse_digits(num) is not None


def _parse_digits(num: Any) -> float | None:
    num = _regex.sub(",", "", str(num))
    try:
        return float(num)
    except ValueError:
        if num.endswith("%"):
            num = num[:-1]
            if num.endswith("\\"):
                num = num[:-1]
            try:
                return float(num) / 100
            except ValueError:
                pass
    return None


def _symbolic_equal(a: Any, b: Any) -> bool:
    def _parse(s):
        for f in [parse_latex, parse_expr]:
            try:
                return f(s)
            except Exception as e:
                logger.debug(f"{f.__name__} failed to parse {s!r}: {e}")
        return s

    a = _parse(a)
    b = _parse(b)
    try:
        if simplify(a - b) == 0:
            return True
    except Exception as e:
        logger.debug(f"sympy simplify failed for {a!r} - {b!r}: {e}")
    try:
        from math import isclose

        if isclose(N(a), N(b), abs_tol=1e-4):
            return True
    except Exception as e:
        logger.debug(f"Numeric comparison failed for {a!r}, {b!r}: {e}")
    return False


def math_equal(prediction: Any, reference: Any) -> bool:
    """Check if prediction equals reference using symbolic math comparison."""
    if str(prediction) == str(reference):
        return True
    if _is_digit(prediction) and _is_digit(reference):
        prediction = _parse_digits(prediction)
        reference = _parse_digits(reference)
        from math import isclose

        return isclose(prediction, reference, abs_tol=1e-4)
    return _symbolic_equal(prediction, reference)


def calculate_math_score(expected_output: str, prediction: str) -> Tuple[int, str]:
    """Calculate score for MATH dataset."""
    if not isinstance(expected_output, str):
        expected_output = str(expected_output)
    if not isinstance(prediction, str):
        prediction = str(prediction)
    expected_answer = extract_model_answer_math(expected_output)
    predicted_answer = extract_model_answer_math(prediction)
    if math_equal(predicted_answer, expected_answer):
        return 1, predicted_answer
    return 0, predicted_answer


# ---------------------------------------------------------------------------
# GPQA scoring
# ---------------------------------------------------------------------------


def format_gpqa_with_choices(item: Dict[str, Any]) -> Tuple[str, str]:
    """Format a GPQA problem with shuffled choices. Returns (formatted_question, correct_letter)."""
    question = item.get("Question", "")
    correct_answer = item.get("Correct Answer", "")
    incorrect_1 = item.get("Incorrect Answer 1", "")
    incorrect_2 = item.get("Incorrect Answer 2", "")
    incorrect_3 = item.get("Incorrect Answer 3", "")

    choices = [correct_answer, incorrect_1, incorrect_2, incorrect_3]

    # Deterministic shuffle based on question hash
    question_hash = hash(question) % 24
    if question_hash % 4 == 0:
        choice_order = [0, 1, 2, 3]
    elif question_hash % 4 == 1:
        choice_order = [1, 0, 2, 3]
    elif question_hash % 4 == 2:
        choice_order = [1, 2, 0, 3]
    else:
        choice_order = [1, 2, 3, 0]

    correct_letter = chr(65 + choice_order.index(0))

    formatted_question = f"{question}\n\n"
    for i, choice_idx in enumerate(choice_order):
        letter = chr(65 + i)
        formatted_question += f"{letter}. {choices[choice_idx]}\n"

    return formatted_question, correct_letter


def extract_model_answer_gpqa(text: str) -> Optional[str]:
    """Extract answer choice (A, B, C, D) from model response."""
    if not isinstance(text, str):
        text = str(text)

    # First, try to extract from SelfConsistency <voted> tags
    voted_pattern = r"<voted><!\[CDATA\[(.*?)\]\]></voted>"
    voted_matches = re.findall(voted_pattern, text, re.DOTALL | re.IGNORECASE)
    if voted_matches:
        voted_text = voted_matches[-1]
        vote_patterns = [
            r"(?:answer|choice)\s*(?:is|:)\s*([ABCD])",
            r"\b([ABCD])\s*(?:is\s+(?:the\s+)?(?:correct|right|answer))",
            r"(?:^|\s)([ABCD])(?:\s*[.)]|\s*$)",
            r"\(([ABCD])\)",
            r"option\s+([ABCD])",
            r"choice\s+([ABCD])",
        ]
        for pattern in vote_patterns:
            matches = re.findall(pattern, voted_text, re.IGNORECASE)
            if matches:
                return matches[-1].upper()

    # Fallback to original patterns
    patterns = [
        r"(?:answer|choice)\s*(?:is|:)\s*([ABCD])",
        r"\b([ABCD])\s*(?:is\s+(?:the\s+)?(?:correct|right|answer))",
        r"(?:^|\s)([ABCD])(?:\s*[.)]|\s*$)",
        r"\(([ABCD])\)",
        r"option\s+([ABCD])",
        r"choice\s+([ABCD])",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[-1].upper()

    # Last resort: last occurrence of A, B, C, or D
    matches = re.findall(r"\b([ABCD])\b", text)
    if matches:
        return matches[-1].upper()

    return None


def calculate_gpqa_score(expected_answer: str, predicted_answer: Optional[str]) -> Tuple[float, str]:
    """Calculate score based on answer choice match."""
    if predicted_answer is None:
        return 0.0, "None"
    score = 1.0 if predicted_answer.upper() == expected_answer.upper() else 0.0
    return score, predicted_answer


# ---------------------------------------------------------------------------
# HumanEval scoring
# ---------------------------------------------------------------------------


def _strip_xml_and_meta(text: str) -> str:
    s = str(text)
    s = re.sub(r"```xml\s*[\s\S]*?```", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"</?[A-Za-z][A-Za-z0-9:_-]*(?:\s+[^<>]*?)?>", " ", s)
    return s


def _extract_code_blocks(text: str) -> list[str]:
    blocks = re.findall(r"```[a-zA-Z_]*\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    return [b.strip() for b in blocks if b and b.strip()]


def _extract_xml_code_blocks(text: str) -> list[str]:
    s = str(text)
    out: list[str] = []
    for tag in ["final_answer", "code", "solution", "updated_code"]:
        m = re.findall(rf"<{tag}>\s*(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?\s*</{tag}>", s, flags=re.IGNORECASE)
        for blk in m or []:
            if blk and blk.strip():
                out.append(blk.strip())
    return out


def _pick_block_with_entry(blocks: list[str], entry_point: str) -> str | None:
    for blk in blocks:
        if re.search(rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\(", blk, flags=re.MULTILINE):
            return blk.strip()
    for blk in blocks:
        if re.search(r"^\s*(?:async\s+)?def\s+[A-Za-z_][A-Za-z0-9_]*\s*\(", blk, flags=re.MULTILINE):
            return blk.strip()
    return blocks[-1].strip() if blocks else None


def _slice_function_by_regex(text: str, entry_point: str) -> str | None:
    m = re.search(
        rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\([^\)]*\)\s*:[\s\S]*?(?=^\s*def\s+[A-Za-z_]|^\s*async\s+def\s+[A-Za-z_]|\Z)",
        text,
        flags=re.MULTILINE,
    )
    if m:
        return m.group(0).strip()
    return None


def _isolate_function_from_text(text: str, entry_point: str) -> str:
    import ast

    s = str(text)
    lines = s.splitlines()
    try:
        tree = ast.parse(s)
    except (SyntaxError, ValueError):
        return s
    include_ranges = []
    for node in getattr(tree, "body", []) or []:
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            start = getattr(node, "lineno", None)
            end = getattr(node, "end_lineno", None)
            if start is not None:
                sidx = max(0, int(start) - 1)
                eidx = int(end) if end is not None else sidx + 1
                include_ranges.append((sidx, eidx))
    if not include_ranges:
        return s
    include_ranges.sort()
    merged = []
    for a, b in include_ranges:
        if not merged or a > merged[-1][1]:
            merged.append((a, b))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
    parts = ["\n".join(lines[a:b]) for a, b in merged]
    return "\n\n".join(p.strip("\n") for p in parts if p.strip()).strip()


def _extract_exact_signature_from_prompt(prompt_text: str, entry_point: str) -> str | None:
    m = re.search(
        rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\([^\)]*\)\s*:",
        str(prompt_text),
        flags=re.MULTILINE,
    )
    return m.group(0) if m else None


def _enforce_exact_signature(code: str, entry_point: str, prompt_text: str) -> str:
    exact = _extract_exact_signature_from_prompt(prompt_text, entry_point)
    if not exact:
        return code
    if re.search(rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\(", code, flags=re.MULTILINE):
        return re.sub(
            rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\([^\)]*\)\s*:",
            exact,
            code,
            count=1,
            flags=re.MULTILINE,
        )
    return f"{exact}\n\tpass\n\n{code.strip()}"


def prepare_humaneval_code(raw_text: str, entry_point: str, prompt_text: str) -> str:
    """Multi-step code extraction for HumanEval."""
    from experiments.lib.eval_utils import _extract_string_from_output

    s = _extract_string_from_output(raw_text)
    blocks = _extract_code_blocks(s)
    if not blocks:
        blocks = _extract_xml_code_blocks(s)
    chosen = _pick_block_with_entry(blocks, entry_point) if blocks else None
    if not chosen:
        s2 = _strip_xml_and_meta(s)
        if re.search(rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\(", s2, flags=re.MULTILINE):
            chosen = s2
        else:
            chosen = _slice_function_by_regex(s2, entry_point) or s2
    if chosen:
        chosen = _isolate_function_from_text(chosen, entry_point)
    chosen = re.sub(r"^```[a-zA-Z]*\n|```$", "", chosen).strip()
    chosen = _enforce_exact_signature(chosen, entry_point, prompt_text or "")
    return chosen


class _TimeoutError(Exception):
    pass


def _run_with_timeout(func: Callable[..., Any], args: tuple[Any, ...], timeout: float) -> Any:
    result: list[Any] = []
    stop_event = threading.Event()

    def target() -> None:
        try:
            result.append(func(*args))
        except Exception as e:
            logger.debug(f"Exception in test execution thread: {e}")
            result.append(e)
        finally:
            stop_event.set()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    is_timeout = not stop_event.wait(timeout)
    if is_timeout:
        raise _TimeoutError("Function execution timed out")
    if not result:
        return None
    if isinstance(result[0], Exception):
        raise result[0]
    return result[0]


def check_solution(solution: str, test: str, entry_point: str, timeout: int = 15) -> Tuple[str, str]:
    """Execute test code against a HumanEval solution."""
    try:
        from typing import Any, Dict, List, Optional, Tuple as Tup

        solution = sanitize(code=solution, entrypoint=entry_point)
        global_dict = {
            "math": __import__("math"),
            "hashlib": __import__("hashlib"),
            "re": __import__("re"),
            "List": List,
            "Dict": Dict,
            "Tuple": Tup,
            "Optional": Optional,
            "Any": Any,
        }
        if entry_point == "decode_cyclic":
            solution = (
                '\n\ndef encode_cyclic(s: str):\n    """\n    returns encoded string by cycling groups of three characters.\n    """\n    groups = [s[(3 * i):min((3 * i + 3), len(s))] for i in range((len(s) + 2) // 3)]\n    groups = [(group[1:] + group[0]) if len(group) == 3 else group for group in groups]\n    return "".join(groups)'
                + "\n\n"
                + solution
            )
        elif entry_point == "decode_shift":
            solution = (
                '\n\ndef encode_shift(s: str):\n    """\n    returns encoded string by shifting every character by 5 in the alphabet.\n    """\n    return "".join([chr(((ord(ch) + 5 - ord("a")) % 26) + ord("a")) for ch in s])\n\n\n'
                + solution
            )
        elif entry_point == "find_zero":
            solution = (
                "\n\ndef poly(xs: list, x: float):\n    return sum(coeff * (x ** i) for i, coeff in enumerate(xs))\n\n"
                + solution
            )
        exec(solution, global_dict)
        if entry_point not in global_dict:
            raise ValueError(f"Function {entry_point} is not defined in the solution.")
        exec(test, global_dict)
        check = global_dict["check"]
        result = _run_with_timeout(check, (global_dict[entry_point],), timeout)
        if result is None:
            result = ("PASS", "The solution passed all test cases.")
        return result
    except _TimeoutError:
        logger.debug(f"HumanEval solution for {entry_point} timed out")
        return ("FAIL", "Execution timed out.")
    except Exception as e:
        logger.debug(f"HumanEval solution for {entry_point} failed: {e}")
        return ("FAIL", f"Error: {str(e)}.")


# ---------------------------------------------------------------------------
# MMLU scoring
# ---------------------------------------------------------------------------


def format_mmlu_question(item: Dict[str, Any]) -> str:
    """Format MMLU question with choices."""
    question = item.get("question", "")
    choices = item.get("choices", [])
    if choices:
        choice_text = "\n".join([f"{chr(65 + i)}. {choice}" for i, choice in enumerate(choices)])
        return f"{question}\n\n{choice_text}"
    else:
        return question


def extract_answer_letter(response: str) -> str:
    """Extract the answer letter (A, B, C, D) from the response."""
    response_str = str(response)

    patterns = [
        r"The\s+final\s+answer\s+is[:\s]*([A-D])",
        r"<final_answer>.*?The\s+final\s+answer\s+is[:\s]*([A-D]).*?</final_answer>",
        r"final\s+answer[:\s]*([A-D])",
        r"answer[:\s]*([A-D])\s*$",
        r"([A-D])\s*$",
        r"[:.]\s*([A-D])\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, response_str, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).upper()

    return ""


def calculate_mmlu_score(expected_answer: int, predicted_letter: str) -> Tuple[float, str]:
    """Calculate score for MMLU question. expected_answer is int index (0-3)."""
    if not predicted_letter:
        return 0.0, ""
    predicted_index = ord(predicted_letter) - ord("A")
    score = 1.0 if predicted_index == expected_answer else 0.0
    return score, predicted_letter
