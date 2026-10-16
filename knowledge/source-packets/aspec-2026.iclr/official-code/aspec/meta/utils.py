import os
import re

from loguru import logger

from aspec.meta.types import OperatorPool, OperatorSpec


def load_prompts_from_file(file_path: str) -> dict[str, str]:
    """Load all prompts from a Python file containing *_PROMPT assignments."""
    import ast

    prompts: dict[str, str] = {}
    if not os.path.exists(file_path):
        logger.warning(f"Prompt file does not exist: {file_path}")
        return prompts

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.endswith("_PROMPT"):
                        if isinstance(node.value, ast.Constant):
                            prompts[target.id] = node.value.value

        return prompts

    except (OSError, SyntaxError, ValueError) as e:
        logger.error(f"Error loading prompts: {e}")
        return prompts


def load_all_operator_prompts(log_path: str) -> dict[str, str]:
    """Load all operator prompts from the prompt file."""
    parent_dir = os.path.dirname(log_path)
    prompt_file_path = os.path.join(parent_dir, "template", "op_prompt.py")
    return load_prompts_from_file(prompt_file_path)


def get_specialized_prompts_file_path(log_path: str) -> str:
    parent_dir = os.path.dirname(log_path)
    return os.path.join(parent_dir, "template", "specialized_prompts.json")


def load_specialized_prompts_from_memory(memory_dir: str) -> OperatorPool:
    """Load specialized operator prompts by parsing specialist memory .md files."""
    result: OperatorPool = {}
    try:
        from pathlib import Path as _Path

        mem_path = _Path(memory_dir)
        if not mem_path.exists() or not mem_path.is_dir():
            return result
        for file in mem_path.glob("*.md"):
            op_name = file.stem
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except OSError as e:
                logger.warning(f"Failed to read memory file {file}: {e}")
                continue
            if not text.strip():
                continue
            base_template = op_name.split("_")[0] if "_" in op_name else op_name
            entry: OperatorSpec = {
                "base_template": base_template,
                "prompt": text.strip(),
            }
            result[op_name] = entry
    except (ImportError, OSError) as e:
        logger.error(f"Error loading specialized prompts from memory files: {e}")
    return result


def extract_xml_components(xml_string: str) -> dict[str, str]:
    """Extract components from an XML string from an LLM response."""
    cleaned_string = xml_string.strip()
    # Strip code fences
    for prefix in ("```xml", "```json", "```"):
        if cleaned_string.startswith(prefix):
            cleaned_string = cleaned_string[len(prefix) :]
            break
    if cleaned_string.endswith("```"):
        cleaned_string = cleaned_string[:-3]
    cleaned_string = cleaned_string.strip()

    def find_tag_content(tag: str, text: str) -> str | None:
        pattern = re.compile(rf"<{tag}>(?:\s*<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</{tag}>", re.DOTALL | re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        return None

    data: dict[str, str] = {}
    tags_to_extract = [
        "action",
        "reasoning",
        "new_operator_name",
        "base_template",
        "new_prompt",
        "target_operator",
        "target_operator_1",
        "target_operator_2",
        "architecture",
        "identity",
        "directives",
    ]

    response_match = re.search(r"<response>(.*?)</response>", cleaned_string, re.DOTALL | re.IGNORECASE)
    search_text = response_match.group(1) if response_match else cleaned_string

    for tag in tags_to_extract:
        content = find_tag_content(tag, search_text)
        if content:
            data[tag] = content

    if "new_prompt" not in data:
        cdata_match = re.search(
            r"<new_prompt>\s*<!\[CDATA\[(.*?)(?:$|</\w+>)", cleaned_string, re.DOTALL | re.IGNORECASE
        )
        if cdata_match:
            data["new_prompt"] = cdata_match.group(1).strip()

    # Extract specialist_prompt nested fields
    if ("identity" not in data) or ("directives" not in data):
        sp_block = re.search(r"<specialist_prompt>(.*?)</specialist_prompt>", cleaned_string, re.DOTALL | re.IGNORECASE)
        if sp_block:
            inner = sp_block.group(1)
            ident = find_tag_content("identity", inner)
            dirs = find_tag_content("directives", inner)
            if ident and ident.strip():
                data["identity"] = ident.strip()
            if dirs and dirs.strip():
                data["directives"] = dirs.strip()

    if "new_prompt" in data and data["new_prompt"] and "{problem}" not in data["new_prompt"]:
        data["new_prompt"] += "\n\nThe problem is: {problem}"

    # Infer action when possible
    if not data.get("action"):
        if data.get("architecture") is not None:
            data["action"] = "FINALIZE_ARCHITECTURE"
        elif data.get("target_operator_1") and data.get("target_operator_2") and data.get("new_operator_name"):
            data["action"] = "COMBINE_OPERATORS"
        elif (
            data.get("new_operator_name")
            and data.get("base_template")
            and (data.get("directives") or data.get("new_prompt"))
        ):
            data["action"] = "CREATE_OPERATOR"
        elif data.get("target_operator") and not data.get("new_prompt"):
            data["action"] = "INSPECT_OPERATOR"

    if not data.get("action"):
        action_match = re.search(r"<action>(.*?)</action>", cleaned_string, re.DOTALL | re.IGNORECASE)
        if action_match:
            data["action"] = action_match.group(1).strip()
        else:
            raise ValueError("Critical field 'action' could not be extracted from the LLM response.")

    return data
