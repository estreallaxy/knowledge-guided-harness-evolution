"""Markdown file backend — the original on-disk storage format."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from loguru import logger

from .. import parser
from ..schema import MemoryDocument


class MarkdownFileBackend:
    """Read/write specialist memory as ``.md`` markdown files."""

    def __init__(self, memory_dir: Path) -> None:
        self.memory_dir = Path(memory_dir)

    # --- helpers ---------------------------------------------------------------

    def _path_for(self, operator_name: str) -> Path:
        file_safe = operator_name.replace("/", "_")
        return self.memory_dir / f"{file_safe}.md"

    # --- MemoryBackend protocol ------------------------------------------------

    def load(self, operator_name: str) -> MemoryDocument | None:
        path = self._path_for(operator_name)
        if not path.exists():
            return None
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            return parser.parse(text, operator_name)
        except OSError as e:
            logger.warning(f"Failed to load memory for {operator_name}: {e}")
            return None

    def save(self, doc: MemoryDocument) -> None:
        path = self._path_for(doc.operator_name)
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            text = parser.serialize(doc)
            path.write_text(text, encoding="utf-8")
        except OSError as e:
            logger.error(f"Failed to save memory for {doc.operator_name}: {e}")

    def exists(self, operator_name: str) -> bool:
        return self._path_for(operator_name).exists()

    def delete(self, operator_name: str) -> None:
        path = self._path_for(operator_name)
        try:
            if path.exists():
                path.unlink()
                logger.info(f"Deleted memory file: {path}")
            # Also cleanup backups
            backup_dir = self.memory_dir / "backups"
            if backup_dir.exists():
                for backup_file in backup_dir.glob(f"{operator_name}_*.md"):
                    try:
                        backup_file.unlink()
                        logger.info(f"Deleted backup file: {backup_file}")
                    except OSError as e:
                        logger.warning(f"Failed to delete backup {backup_file}: {e}")
        except OSError as e:
            logger.warning(f"Failed to delete memory for {operator_name}: {e}")

    def list_specialists(self) -> list[str]:
        if not self.memory_dir.exists():
            return []
        return [p.stem for p in self.memory_dir.glob("*.md") if p.is_file()]

    def archive(self, operator_name: str, tag: str) -> None:
        path = self._path_for(operator_name)
        if not path.exists():
            logger.warning(f"Archive requested but memory file not found for {operator_name}: {path}")
            return
        try:
            backup_dir = self.memory_dir / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = backup_dir / f"{operator_name}_{tag}_{ts}.md"
            try:
                path.replace(archive_path)
            except OSError:
                archive_path.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                path.unlink(missing_ok=True)
            logger.info(f"Archived specialist memory {operator_name} -> {archive_path}")
        except OSError as e:
            logger.warning(f"Failed to archive memory for {operator_name}: {e}")

    # --- Raw file access (for operations that need raw text) -------------------

    def read_raw(self, operator_name: str) -> str:
        """Read raw text from the memory file.  Returns empty string if not found."""
        path = self._path_for(operator_name)
        if not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

    def write_raw(self, operator_name: str, text: str) -> None:
        """Write raw text to the memory file."""
        path = self._path_for(operator_name)
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        except OSError as e:
            logger.error(f"Failed to write raw memory for {operator_name}: {e}")

    def append_raw(self, operator_name: str, text: str) -> None:
        """Append raw text to the memory file."""
        path = self._path_for(operator_name)
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(text)
        except OSError as e:
            logger.error(f"Failed to append to memory for {operator_name}: {e}")

    def get_path(self, operator_name: str) -> Path:
        """Return the filesystem path for an operator's memory file."""
        return self._path_for(operator_name)
