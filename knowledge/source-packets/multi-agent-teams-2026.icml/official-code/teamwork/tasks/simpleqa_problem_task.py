"""SimpleQA Problem Task implementation."""

from typing import Optional

from teamwork.tasks.collaborative_short_answer_task import CollaborativeShortAnswerTask


class SimpleQAProblemTask(CollaborativeShortAnswerTask):
    """Task representing a single problem from the SimpleQA Verified dataset.
    
    This class handles a specific short-answer question instance, providing the
    question text and ground truth extraction logic.
    """

    def __init__(
        self,
        agent_ids: list[int],
        max_rounds: int,
        problem_data: dict,
        unique_id: str | int,
        seed: int | None = None,
        decision_mode: str = "expert_not_mentioned",
        most_capable_model_name: Optional[str] = None,
        use_llm_fallback: bool = True,
        llm_fallback_model: str = "gpt-5-2025-08-07",
        llm_fallback_api_key: Optional[str] = None,
    ):
        """Initialize the SimpleQA problem task.

        Args:
            agent_ids: List of participating agent IDs.
            max_rounds: Maximum rounds of collaboration.
            problem_data: Dictionary containing 'problem' (question), 'answer', and 'original_index' fields.
            unique_id: Unique identifier for this problem instance (should be original_index).
            seed: Random seed for this specific task instance.
            decision_mode: Collaboration strategy.
            most_capable_model_name: Fallback expert model name.
            use_llm_fallback: Whether to use LLM autorating for equivalence checking.
            llm_fallback_model: Model name for LLM autorating (e.g., "gpt-5-2025-08-07").
            llm_fallback_api_key: OpenAI API key for LLM autorating.
        """
        super().__init__(
            agent_ids=agent_ids,
            max_rounds=max_rounds,
            seed=seed,
            decision_mode=decision_mode,
            most_capable_model_name=most_capable_model_name,
            name=f"SimpleQA-{unique_id}",
            use_llm_fallback=use_llm_fallback,
            llm_fallback_model=llm_fallback_model,
            llm_fallback_api_key=llm_fallback_api_key,
        )
        
        self.question_text = problem_data.get('problem', '')
        self.answer = problem_data.get('answer', '')  # May be range, name, date, etc.
        self.unique_id = unique_id

    def get_task_description(self, agent_id: int) -> str:
        """Return the task description (question) for a specific agent."""
        return f"""You are an expert working on a team to answer a short-answer question.

{self.question_text}

Please analyze this question carefully. You must show your reasoning step-by-step.
On a new line, you MUST end your response with 'My answer is X' where X is your final answer.
"""

    def get_ground_truth(self) -> str:
        """Return the ground truth answer from the dataset (may be range, name, date, etc.)."""
        return str(self.answer).strip()

