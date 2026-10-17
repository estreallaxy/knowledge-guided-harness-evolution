"""GPQA Diamond Problem Task implementation."""

from typing import Optional

from teamwork.tasks.collaborative_multiple_choice_task import CollaborativeMultipleChoiceQuestionTask


class GPQADiamondProblemTask(CollaborativeMultipleChoiceQuestionTask):
    """Task representing a single problem from the GPQA Diamond dataset.
    
    This class handles a specific multiple choice question instance, providing the
    question text with embedded options and ground truth extraction logic.
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
        """Initialize the GPQA Diamond problem task.

        Args:
            agent_ids: List of participating agent IDs.
            max_rounds: Maximum rounds of collaboration.
            problem_data: Dictionary containing 'question' and 'answer' fields.
            unique_id: Unique identifier for this problem instance.
            seed: Random seed for this specific task instance.
            decision_mode: Collaboration strategy.
            most_capable_model_name: Fallback expert model name.
            use_llm_fallback: Whether to use LLM as final fallback for equivalence checking.
            llm_fallback_model: Model name for LLM fallback (e.g., "gpt-4o", "gpt-5-2025-08-07").
            llm_fallback_api_key: OpenAI API key for LLM fallback.
        """
        super().__init__(
            agent_ids=agent_ids,
            max_rounds=max_rounds,
            seed=seed,
            decision_mode=decision_mode,
            most_capable_model_name=most_capable_model_name,
            name=f"GPQADiamond-{unique_id}",
            use_llm_fallback=use_llm_fallback,
            llm_fallback_model=llm_fallback_model,
            llm_fallback_api_key=llm_fallback_api_key,
        )
        
        self.question_text = problem_data.get('question', '')
        self.answer = problem_data.get('answer', '')  # Should be letter A, B, C, or D
        self.unique_id = unique_id

    def get_task_description(self, agent_id: int) -> str:
        """Return the task description (question with embedded options) for a specific agent."""
        return f"""You are an expert working on a team to answer a multiple choice question.

{self.question_text}

Please analyze this question carefully. You must show your reasoning step-by-step.
Your final answer must be EXACTLY just the capitalized letter (A, B, C, or D) corresponding to the correct option.
"""

    def get_ground_truth(self) -> str:
        """Return the ground truth answer letter (A, B, C, or D)."""
        # Answer is already A, B, C, or D - no conversion needed
        return str(self.answer).strip().upper()

