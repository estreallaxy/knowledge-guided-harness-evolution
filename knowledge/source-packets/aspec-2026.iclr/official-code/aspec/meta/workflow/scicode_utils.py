import ast
import contextlib
import re

from loguru import logger


class SciCodeWorkflowUtils:
    """Utility class containing SciCode-specific workflow helpers."""

    @staticmethod
    def extract_code_from_react_trajectory(trajectory: str) -> str:
        """Extract code from ReAct trajectory format."""
        try:
            if not trajectory:
                return ""

            # Try standard <step> format first
            steps = re.findall(r"<step>([\s\S]*?)</step>", trajectory, re.DOTALL | re.IGNORECASE)
            if steps:
                for block in reversed(steps):
                    if re.search(r"<action>\s*finish\s*</action>", block, re.IGNORECASE):
                        m = re.search(r"<input>([\s\S]*?)</input>", block, re.DOTALL | re.IGNORECASE)
                        if not m:
                            continue
                        content = m.group(1).strip()
                        # Expect raw Python code (no markdown blocks) in <input> tags
                        if any(tok in content for tok in ["def ", "return ", "class ", "import "]):
                            clean = re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", "", content, flags=re.IGNORECASE)
                            return clean.strip()

            # Try markdown-style step format (```step ... ```) - handle both closed and unclosed
            markdown_steps = re.findall(r"```step\s*\n?([\s\S]*?)(?:```|$)", trajectory, re.DOTALL | re.IGNORECASE)
            if markdown_steps:
                for block in reversed(markdown_steps):
                    if re.search(r"<action>\s*finish\s*</action>", block, re.IGNORECASE):
                        m = re.search(r"<input>\s*\n?([\s\S]*?)\s*</input>", block, re.DOTALL | re.IGNORECASE)
                        if not m:
                            continue
                        content = m.group(1).strip()
                        # First try to extract from nested ```python blocks
                        code_match = re.search(r"```python\s*\n?([\s\S]*?)```", content, re.DOTALL | re.IGNORECASE)
                        if code_match:
                            pick = code_match.group(1).strip()
                            pick = re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", "", pick, flags=re.IGNORECASE)
                            return pick.strip()
                        # Fallback: check for raw Python code in <input> tags
                        if any(tok in content for tok in ["def ", "return ", "class ", "import "]):
                            clean = re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", "", content, flags=re.IGNORECASE)
                            return clean.strip()

            return ""
        except Exception as e:
            logger.warning(f"Failed to extract code from ReAct trajectory: {e}")
            return ""

    @staticmethod
    def extract_code_by_func_name(text: str, func_name: str) -> str:
        """Extract code containing a specific function name."""
        try:
            if not text or not func_name:
                return ""
            pattern_blocks = re.findall(r"```(?:[a-zA-Z0-9_]+)?\s*\n?([\s\S]*?)```", text, re.DOTALL | re.IGNORECASE)
            for blk in reversed(pattern_blocks):
                b = blk.strip()
                if re.search(rf"\bdef\s+{re.escape(func_name)}\s*\(", b):
                    clean = re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", "", b, flags=re.IGNORECASE)
                    return clean.strip()
            m = re.search(rf"(def\s+{re.escape(func_name)}\s*\([^)]*\):[\s\S]*)", text, re.IGNORECASE)
            if m:
                candidate = m.group(1).strip()
                candidate = re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", "", candidate, flags=re.IGNORECASE)
                return candidate
            return ""
        except Exception as e:
            logger.warning(f"Failed to extract code by function name '{func_name}': {e}")
            return ""

    @staticmethod
    def validate_scicode_step(
        code: str, prompt: str, problem_id: str = "", previous_code: str = ""
    ) -> tuple[bool, str]:
        """Validate that the generated code defines required functions and has valid syntax."""
        if not code:
            return False, "No code to validate"

        is_valid = False
        feedback = "Validation passed."

        # Pre-clean: if wrappers leaked in, try to salvage the raw python code
        try:
            c = str(code or "")
            blocks = re.findall(r"```(?:python|py)?\s*\n?([\s\S]*?)```", c, re.IGNORECASE)
            if blocks:
                code = blocks[-1].strip()
            else:
                m = re.search(
                    r"<final_answer>[\s\S]*?```(?:python|py)?\s*\n?([\s\S]*?)```[\s\S]*?</final_answer>",
                    c,
                    re.IGNORECASE,
                )
                if m:
                    code = m.group(1).strip()
                else:
                    # Strip simple XML-ish tags if present
                    code = re.sub(r"<[/]?[a-zA-Z][^>]*>", "", c).strip()
        except Exception as e:
            logger.warning(f"Failed to pre-clean scicode step code: {e}")
            code = str(code or "").strip()

        try:
            parsed = ast.parse(code)
        except SyntaxError:
            try:
                indented_code = "\n".join(["    " + line for line in code.splitlines()])
                parsed = ast.parse(f"def dummy_wrapper():\n{indented_code}")
            except SyntaxError as e:
                return False, f"Syntax error even after wrapping: {e}. Use XML, not JSON!"

        try:
            # sanitize prompt: remove fenced code blocks to avoid picking example headers (e.g., def foo())
            _prompt_clean = re.sub(r"```[\s\S]*?```", "", str(prompt or ""), flags=re.MULTILINE)
            func_header_matches = re.findall(r"^\s*def\s+(\w+)\s*\([^)]*\):", _prompt_clean, re.MULTILINE)
            if func_header_matches:
                expected_func_name = func_header_matches[-1]
                # extract expected parameter list from the function header in the prompt
                param_match = re.search(
                    rf"^\s*def\s+{re.escape(expected_func_name)}\s*\(([^)]*)\):", _prompt_clean, re.MULTILINE
                )
                expected_params = []
                if param_match:
                    params_str = param_match.group(1).strip()
                    if params_str:
                        # split on commas, strip annotations/defaults
                        raw_params = [p.strip() for p in params_str.split(",")]
                        for p in raw_params:
                            name = p.split(":", 1)[0].split("=", 1)[0].strip()
                            # Handle *args and **kwargs by removing the * prefix
                            if name.startswith("**"):
                                name = name[2:]
                            elif name.startswith("*"):
                                name = name[1:]
                            if name:
                                expected_params.append(name)
                defined_functions = [node.name for node in ast.walk(parsed) if isinstance(node, ast.FunctionDef)]

                if expected_func_name in defined_functions:
                    # additionally validate signature arity matches expected header (when available)
                    func_nodes = [
                        node
                        for node in ast.walk(parsed)
                        if isinstance(node, ast.FunctionDef) and node.name == expected_func_name
                    ]
                    fn = func_nodes[0] if func_nodes else None
                    if fn and expected_params:
                        actual_params = [a.arg for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs]
                        # Include *args and **kwargs in parameter count
                        if fn.args.vararg:
                            actual_params.append(fn.args.vararg.arg)
                        if fn.args.kwarg:
                            actual_params.append(fn.args.kwarg.arg)
                        if len(actual_params) != len(expected_params):
                            return (
                                False,
                                f"Signature mismatch for '{expected_func_name}': expected {len(expected_params)} args ({', '.join(expected_params)}), got {len(actual_params)} ({', '.join(actual_params)})",
                            )
                    is_valid = True
                    feedback = f"Required function '{expected_func_name}' found."
                else:
                    if previous_code:
                        try:
                            previous_parsed = ast.parse(previous_code)
                            if any(
                                node.name == expected_func_name
                                for node in ast.walk(previous_parsed)
                                if isinstance(node, ast.FunctionDef)
                            ):
                                is_valid = True
                                feedback = f"Required function '{expected_func_name}' found in previous code."
                        except SyntaxError:
                            pass

                    if not is_valid:
                        feedback = f"Required function '{expected_func_name}' not defined. Found: {defined_functions}"
                        return False, feedback
            else:
                is_valid = True
                feedback = "No specific function header found in prompt to validate against."

        except Exception as e:
            logger.warning(f"Validation error while checking scicode step: {e}")
            return False, f"Validation error: {e}"

        return is_valid, feedback

    @staticmethod
    def _allowed_modules_from_block(block_text: str) -> set[str]:
        mods: set[str] = set()
        with contextlib.suppress(Exception):
            mods = SciCodeWorkflowUtils._parse_imported_modules(block_text)
        return mods
