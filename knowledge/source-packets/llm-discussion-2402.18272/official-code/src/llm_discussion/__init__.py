"""Conquer-and-Merge Discussion with OpenRouter and offline dry runs."""

from .types import ChatMessage, Completion, DiscussionConfig, Request, Result, Task
from .engine import run_discussion

__all__ = ["ChatMessage", "Completion", "DiscussionConfig", "Request", "Result", "Task", "run_discussion"]
__version__ = "0.2.0"
