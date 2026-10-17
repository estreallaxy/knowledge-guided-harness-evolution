import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class TrajectoryRecorder:
    """Utility class to persist prompts, responses and scores to JSONL."""

    _instance = None

    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"trajectory/datasets/{timestamp}.jsonl"
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.file_path, "a", encoding="utf-8")

    @classmethod
    def instance(cls) -> Optional["TrajectoryRecorder"]:
        path = os.environ.get("TRAJECTORY_FILE")
        if cls._instance is None and path is not None:
            cls._instance = cls(path)
        return cls._instance

    def record(self, data: dict) -> None:
        json_line = json.dumps(data, ensure_ascii=False)
        self.file.write(json_line + "\n")
        self.file.flush()

    def close(self) -> None:
        if not self.file.closed:
            self.file.close()

