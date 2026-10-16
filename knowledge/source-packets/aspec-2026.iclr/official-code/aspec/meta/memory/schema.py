"""Data model for the specialist memory system."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MemorySection(Enum):
    SPECIALIST_PROMPT = "Specialist Prompt"
    STRUCTURED_MEMORY_ENTRY = "Structured Memory Entry"
    LATEST_EXECUTION_ROUND = "Latest Execution Round"
    POST_EXECUTION_REFLECTION = "Post-Execution Reflection"
    IMPORTED_MEMORY = "Imported Memory"
    DISTILLED_DIRECTIVES = "Distilled Directives"
    OTHER = "Other"


# Normalized lookup: lowered heading text -> MemorySection
_HEADING_TO_SECTION: dict[str, MemorySection] = {}
for _sec in MemorySection:
    if _sec is not MemorySection.OTHER and _sec is not MemorySection.IMPORTED_MEMORY:
        _HEADING_TO_SECTION[_sec.value.lower()] = _sec


def classify_heading(heading_text: str) -> MemorySection:
    """Classify a ``## Heading`` line into a MemorySection.

    Uses normalized string matching (not regex).  ``heading_text`` should be
    the text *after* stripping the leading ``## `` prefix.
    """
    normalized = heading_text.strip().lower()
    exact = _HEADING_TO_SECTION.get(normalized)
    if exact is not None:
        return exact
    # Imported Memory headings look like "Imported Memory from <op>"
    if normalized.startswith("imported memory"):
        return MemorySection.IMPORTED_MEMORY
    return MemorySection.OTHER


@dataclass
class StructuredMemoryEntry:
    problem_pattern: str = ""
    approach_summary: str = ""
    failure_mode: str = ""
    general_rule: str = ""


@dataclass
class MemoryDocument:
    operator_name: str = ""
    title: str = ""
    specialist_prompt: str = ""
    structured_entries: list[StructuredMemoryEntry] = field(default_factory=list)
    # Catch-all for sections that don't map to a typed field.
    # Each tuple is (full_heading_text, body_text).
    raw_other_sections: list[tuple[str, str]] = field(default_factory=list)

    # --- convenience helpers ---------------------------------------------------

    def get_section(self, section: MemorySection) -> str:
        if section is MemorySection.SPECIALIST_PROMPT:
            return self.specialist_prompt
        if section is MemorySection.STRUCTURED_MEMORY_ENTRY:
            # Return all entries concatenated
            from . import parser as _parser

            parts = []
            for entry in self.structured_entries:
                parts.append(_parser._render_structured_entry(entry))
            return "\n".join(parts)
        # For OTHER / IMPORTED_MEMORY / LATEST_EXECUTION_ROUND / POST_EXECUTION_REFLECTION
        # scan raw_other_sections
        target_label = section.value.lower()
        for heading, body in self.raw_other_sections:
            if heading.strip().lower().startswith(target_label):
                return body
        return ""

    def set_section(self, section: MemorySection, content: str) -> None:
        if section is MemorySection.SPECIALIST_PROMPT:
            self.specialist_prompt = content
        else:
            # Replace or append in raw_other_sections
            target_label = section.value.lower()
            for i, (heading, _body) in enumerate(self.raw_other_sections):
                if heading.strip().lower().startswith(target_label):
                    self.raw_other_sections[i] = (heading, content)
                    return
            self.raw_other_sections.append((section.value, content))

    def has_required_sections(self) -> bool:
        return bool(self.specialist_prompt.strip())
