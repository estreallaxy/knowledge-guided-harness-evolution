"""Abstract storage protocol for specialist memory."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .schema import MemoryDocument


@runtime_checkable
class MemoryBackend(Protocol):
    """Protocol that all memory storage backends must implement."""

    def load(self, operator_name: str) -> MemoryDocument | None:
        """Load a specialist's memory document.  Returns None if not found."""
        ...

    def save(self, doc: MemoryDocument) -> None:
        """Persist a memory document."""
        ...

    def exists(self, operator_name: str) -> bool:
        """Check whether a memory document exists for the given operator."""
        ...

    def delete(self, operator_name: str) -> None:
        """Delete a specialist's memory document."""
        ...

    def list_specialists(self) -> list[str]:
        """Return names of all stored specialists."""
        ...

    def archive(self, operator_name: str, tag: str) -> None:
        """Move the specialist's memory to an archive/backup location."""
        ...
