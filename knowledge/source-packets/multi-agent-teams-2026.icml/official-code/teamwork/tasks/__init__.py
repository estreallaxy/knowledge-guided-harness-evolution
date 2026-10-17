"""Task implementations for multi-agent collaboration experiments."""

from teamwork.tasks.moon_survival_task import MoonSurvivalTask
from teamwork.tasks.task import Task, TaskResult
from teamwork.tasks.collaborative_short_answer_task import CollaborativeShortAnswerTask
from teamwork.tasks.simpleqa_problem_task import SimpleQAProblemTask

__all__ = ["Task", "TaskResult", "MoonSurvivalTask", "CollaborativeShortAnswerTask", "SimpleQAProblemTask"]