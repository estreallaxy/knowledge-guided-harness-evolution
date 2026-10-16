"""Single source of truth for parsing and serializing specialist memory markdown files.

Every other module that needs to read or write memory sections should go through
this module instead of using its own regex patterns.
"""

from __future__ import annotations

import re

from .schema import (
    MemoryDocument,
    MemorySection,
    StructuredMemoryEntry,
    classify_heading,
)

# ---------------------------------------------------------------------------
# The ONE compiled regex used for heading splitting
# ---------------------------------------------------------------------------
_HEADING_RE = re.compile(r"^(#{1,2}\s+.+)$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse(text: str, operator_name: str = "") -> MemoryDocument:
    """Parse a specialist memory markdown string into a ``MemoryDocument``.

    Splits on heading boundaries, classifies each ``## Heading`` into a
    ``MemorySection``, and populates the dataclass.

    If a file has duplicate ``## Specialist Prompt`` sections, the *last*
    occurrence wins (same for Description).
    """
    doc = MemoryDocument(operator_name=operator_name)

    if not text or not text.strip():
        return doc

    # Split the text into (heading, body) pairs.
    parts = _HEADING_RE.split(text)
    # parts is [pre-heading-text, heading1, body1, heading2, body2, ...]

    preamble = parts[0]

    # Check for a title (# line) in the preamble
    title_match = re.match(r"^#\s+(.+)", preamble.strip())
    if title_match:
        doc.title = title_match.group(1).strip()

    # Process heading/body pairs
    i = 1
    while i < len(parts):
        heading_line = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        i += 2

        # Only process ## headings (not the # title)
        if heading_line.startswith("## "):
            heading_text = heading_line[3:].strip()
        elif heading_line.startswith("##"):
            heading_text = heading_line[2:].strip()
        elif heading_line.startswith("# "):
            # This is a title header encountered mid-document; use as title if not set
            if not doc.title:
                doc.title = heading_line[2:].strip()
            continue
        else:
            continue

        section = classify_heading(heading_text)
        body_text = body.strip()

        if section is MemorySection.SPECIALIST_PROMPT:
            doc.specialist_prompt = body_text
        elif section is MemorySection.STRUCTURED_MEMORY_ENTRY:
            entry = _parse_structured_entry(body_text)
            doc.structured_entries.append(entry)
        else:
            # LATEST_EXECUTION_ROUND, POST_EXECUTION_REFLECTION, IMPORTED_MEMORY, OTHER
            doc.raw_other_sections.append((heading_text, body_text))

    return doc


def serialize(doc: MemoryDocument) -> str:
    """Render a ``MemoryDocument`` back to markdown.

    Produces exactly one copy of each typed section.
    """
    parts: list[str] = []

    # Title
    title = doc.title or (doc.operator_name.replace("_", " ") + "'s Memory" if doc.operator_name else "Memory")
    parts.append(f"# {title}")

    # Specialist Prompt
    if doc.specialist_prompt:
        parts.append(f"## Specialist Prompt\n{doc.specialist_prompt}")

    # Structured Memory Entries
    for entry in doc.structured_entries:
        parts.append(_render_structured_entry(entry))

    # Other sections (preserves original ordering)
    for heading, body in doc.raw_other_sections:
        parts.append(f"## {heading}\n{body}")

    return "\n\n".join(parts) + "\n"


def extract_section(text: str, section: MemorySection, operator_name: str = "") -> str:
    """Convenience wrapper: parse text and return a single section's content."""
    doc = parse(text, operator_name)
    return doc.get_section(section)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_structured_entry(body: str) -> StructuredMemoryEntry:
    """Parse the body of a ``## Structured Memory Entry`` into a dataclass."""
    entry = StructuredMemoryEntry()
    for line in body.splitlines():
        ln = line.strip().lstrip("-• ").strip()
        parts = ln.split(":", 1)
        if len(parts) != 2:
            continue
        key, val = parts[0].strip().lower(), parts[1].strip()
        if not val:
            continue
        if "problem" in key and "pattern" in key:
            entry.problem_pattern = val
        elif "approach" in key and "summary" in key:
            entry.approach_summary = val
        elif "failure" in key and "mode" in key:
            entry.failure_mode = val
        elif "general" in key and "rule" in key:
            entry.general_rule = val
    return entry


def _render_structured_entry(entry: StructuredMemoryEntry) -> str:
    """Render a single structured memory entry to markdown."""
    lines: list[str] = ["## Structured Memory Entry"]
    if entry.problem_pattern:
        lines.append(f"- Problem pattern: {entry.problem_pattern}")
    if entry.approach_summary:
        lines.append(f"- Approach summary: {entry.approach_summary}")
    if entry.failure_mode:
        lines.append(f"- Failure mode: {entry.failure_mode}")
    if entry.general_rule:
        lines.append(f"- General rule: {entry.general_rule}")
    return "\n".join(lines)
