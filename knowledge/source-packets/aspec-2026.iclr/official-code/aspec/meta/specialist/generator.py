"""
Specialist Prompt Generation System
Structured identity/directives injection using simple template formatting.
"""

import re

from loguru import logger


def _split_identity(identity: str) -> dict[str, str]:
    s = (identity or "").strip()
    if not s:
        return {"identity_line": "", "identity_clause": "", "identity": ""}
    low = s.lower()
    body = s
    if low.startswith("you are"):
        body = s[7:].strip().lstrip(" .,:-")
    identity_line = f"{s}\n\n"
    identity_clause = f"As {body}, " if body else ""
    return {"identity_line": identity_line, "identity_clause": identity_clause, "identity": body or s}


def create_specialist_prompt(base_prompt_template: str, specialist_data: dict[str, str]) -> str:
    """
    Compose a complete specialist prompt by formatting the base template with identity and directives.
    The base template must contain {identity} and {directives} placeholders.
    """
    identity = specialist_data.get("identity", "") or ""
    directives = specialist_data.get("directives", "") or ""
    parts = _split_identity(identity)

    try:
        formatted_prompt = base_prompt_template
        formatted_prompt = formatted_prompt.replace("{identity_line}", parts.get("identity_line", ""))
        formatted_prompt = formatted_prompt.replace("{identity_clause}", parts.get("identity_clause", ""))
        formatted_prompt = formatted_prompt.replace("{identity}", parts.get("identity", identity))
        formatted_prompt = formatted_prompt.replace("{directives}", directives)
        formatted_prompt = formatted_prompt.replace("{directives_block}", directives or "")
        # Leave {problem} and {context} unfilled - they will be filled later by the operator
        return formatted_prompt
    except AttributeError as e:
        logger.warning(f"Failed to format specialist prompt: {e}")
        return f"{parts.get('identity_line', '')}{directives or ''}\n\n{base_prompt_template}"


def reconstruct_specialist_prompt(
    op_name: str,
    raw_prompt: str,
    dataset: str,
) -> str | None:
    """Reconstruct a complete specialist prompt from raw directives.

    Returns the reconstructed prompt, or None if reconstruction is not needed
    (prompt already formatted) or not possible (no base template found).
    """
    is_already_formatted = (
        "{problem}" in raw_prompt
        and "{context}" in raw_prompt
        and (
            "Think step by step" in raw_prompt
            or "You are" in raw_prompt
            or "Strict answer policy" in raw_prompt
            or "$\\boxed{" in raw_prompt
        )
    )
    if is_already_formatted:
        return None

    base_template = op_name.split("_")[0]
    try:
        from importlib import import_module

        module_path = f"experiments.datasets.{dataset}.train.template.op_prompt"
        op_prompts = import_module(module_path)
        base_prompts: dict[str, str] = {}
        for attr_name in [
            "COT_PROMPT",
            "REACT_PROMPT",
            "DEBATE_PROMPT",
            "SELFCONSISTENCY_PROMPT",
            "ENSEMBLE_MEMBER_PROMPT",
            "ENSEMBLE_RANK_PROMPT",
            "SELFREFINE_PROMPT",
            "TESTING_PROMPT",
        ]:
            if hasattr(op_prompts, attr_name):
                base_prompts[attr_name.replace("_PROMPT", "")] = getattr(op_prompts, attr_name)
    except ImportError as e:
        logger.warning(f"Failed to import prompts for dataset {dataset}: {e}")
        return None

    base_prompt_template = base_prompts.get(base_template.upper())
    if not base_prompt_template:
        return None

    from aspec.meta.models.architect._validation import extract_clean_directives

    clean_directives = extract_clean_directives(raw_prompt)
    specialist_data: dict[str, str] = {"identity": "", "directives": clean_directives}
    return create_specialist_prompt(base_prompt_template, specialist_data)


def extract_specialist_knowledge_from_memory(memory_text: str) -> dict[str, str]:
    """
    Extract specialist knowledge from memory files into structured format.

    Returns:
        Dict with 'identity' and 'directives' keys
    """
    from aspec.meta.memory.parser import parse as _parse

    specialist_data: dict[str, str] = {"identity": "", "directives": ""}

    doc = _parse(memory_text)
    prompt_block = doc.specialist_prompt

    if prompt_block:
        # Identity: first "You are ..." line (up to blank line)
        id_match = re.search(r"(?mi)^\s*You\s+are[\s\S]*?(?:\n\s*\n|$)", prompt_block)
        if id_match:
            specialist_data["identity"] = id_match.group(0).strip()
        # Directives: bullet lines until Problem:/Context:
        directives_lines = []
        for line in prompt_block.splitlines():
            s = line.strip()
            if (
                s.lower().startswith("problem:")
                or s.lower().startswith("{problem}")
                or s.lower().startswith("context:")
            ):
                break
            if s.startswith("-") or s.startswith("•"):
                directives_lines.append(line)
        if directives_lines:
            specialist_data["directives"] = "\n".join(directives_lines).strip()

    if not specialist_data["directives"] and prompt_block:
        cleaned = prompt_block
        if specialist_data["identity"]:
            cleaned = cleaned.replace(specialist_data["identity"], "").strip()
        specialist_data["directives"] = cleaned

    return specialist_data
