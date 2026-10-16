"""LLM-based memory distillation."""

from __future__ import annotations

import re
from typing import Any

from loguru import logger

from . import parser
from .schema import MemoryDocument, MemorySection
from .store import MemoryStore

DISTILL_PROMPT = """
You are the Knowledge Distiller. Extract key insights from specialist memory entries and create concise directives to inject into the specialist's prompt.

Your task:
1. Read all "## Structured Memory Entry" sections
2. Extract recurring patterns, successful approaches, and failure modes
3. Generalize into actionable bullet-point directives (not examples)
4. Keep directives abstract and transferable (avoid specific problem details)

Output format:
```
DISTILLED_DIRECTIVES:
- [Actionable directive based on learned patterns]
- [Another directive from failure modes]
- [Directive about successful approaches]
```

Keep it concise (max 5-8 bullet points). Focus on HOW to think, not WHAT to do for specific problems.
"""


class MemoryDistiller:
    """Distills structured memory entries into actionable directives via LLM."""

    def __init__(self, store: MemoryStore, llm: Any = None, exec_llm: Any = None) -> None:
        self.store = store
        self.llm = llm
        self.exec_llm = exec_llm

    async def distill_and_update(self, op_name: str, epoch: int) -> None:
        """Distill the memory for a specialist and update the memory file."""
        logger.info(f"Distilling memory for {op_name} at epoch {epoch}")
        await self._distill_internal(op_name, epoch)

    async def distill_with_reflections(self, op_name: str, epoch: int) -> None:
        """Distill memory for specialists with post-execution reflections."""
        await self._distill_internal(op_name, epoch)

    async def _distill_internal(self, op_name: str, epoch: int) -> None:
        try:
            doc = self.store.load_document(op_name)
            if doc is None or not doc.structured_entries:
                if doc is None:
                    return
                logger.info(f"No structured memory entries for {op_name}, skipping distillation")
                return

            # Build distillation payload
            entry_texts: list[str] = []
            for entry in doc.structured_entries:
                entry_texts.append(parser._render_structured_entry(entry))

            memory_content = "\n\n".join(entry_texts)
            payload = DISTILL_PROMPT + f"\n\nSpecialist: {op_name}\nMemory entries to distill:\n\n{memory_content}"

            llm = self.exec_llm or self.llm
            if llm is None:
                logger.warning(f"No LLM available for distillation of {op_name}")
                return

            distilled_response = await llm.aask(payload)
            distilled_directives = self._extract_directives(distilled_response)

            if not distilled_directives:
                logger.warning(f"No distilled directives extracted for {op_name}")
                return

            await self._inject_into_prompt(op_name, distilled_directives, doc)
            logger.info(f"Successfully distilled memory and updated prompt for {op_name}")

        except Exception as e:
            logger.error(f"Failed to distill memory for {op_name}: {e}")

    @staticmethod
    def _extract_directives(response: str) -> str:
        """Extract DISTILLED_DIRECTIVES from LLM response."""
        try:
            match = re.search(r"DISTILLED_DIRECTIVES:\s*((?:- .*(?:\n|$))+)", response, re.MULTILINE)
            if match:
                return match.group(1).strip()

            # Fallback: look for bullet points after any mention of directives
            lines = response.split("\n")
            in_directives = False
            directives = []
            for line in lines:
                line = line.strip()
                if "directive" in line.lower() or "DISTILLED_DIRECTIVES" in line:
                    in_directives = True
                    continue
                elif in_directives and line.startswith("- "):
                    directives.append(line)
                elif in_directives and line and not line.startswith("- ") and not line.startswith("#"):
                    break
            return "\n".join(directives) if directives else ""
        except Exception as e:
            logger.warning(f"Failed to extract distilled directives: {e}")
            return ""

    async def _inject_into_prompt(self, op_name: str, distilled_directives: str, doc: MemoryDocument) -> None:
        """Inject distilled insights as a dedicated Distilled Directives section."""
        try:
            doc.set_section(MemorySection.DISTILLED_DIRECTIVES, distilled_directives)
            self.store.save_document(doc)
        except Exception as e:
            logger.error(f"Failed to inject distilled insights for {op_name}: {e}")
