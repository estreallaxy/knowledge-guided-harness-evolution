"""MMLU Pro Problem Task implementation."""

from typing import Optional

from teamwork.tasks.collaborative_multiple_choice_task import CollaborativeMultipleChoiceQuestionTask


class MMLUProProblemTask(CollaborativeMultipleChoiceQuestionTask):
    """Task representing a single problem from the MMLU Pro dataset.
    
    This class handles a specific multiple choice question instance, providing the
    question text with formatted options and ground truth extraction logic.
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
        """Initialize the MMLU Pro problem task.

        Args:
            agent_ids: List of participating agent IDs.
            max_rounds: Maximum rounds of collaboration.
            problem_data: Dictionary containing 'question_id', 'question', 'options' (list of 10), 'answer'.
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
            name=f"MMLUPro-{unique_id}",
            use_llm_fallback=use_llm_fallback,
            llm_fallback_model=llm_fallback_model,
            llm_fallback_api_key=llm_fallback_api_key,
        )
        
        self.question_id = problem_data.get('question_id', '')
        self.question_text = problem_data.get('question', '')
        self.options = problem_data.get('options', [])  # List of 10 options
        self.answer = problem_data.get('answer', '')  # Should be letter A-J or index
        self.unique_id = unique_id

    def get_task_description(self, agent_id: int) -> str:
        """Return the task description (question + formatted options) for a specific agent."""
        # Format options as A-J
        options_text = ""
        option_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        
        for i, option in enumerate(self.options):
            if i < len(option_letters):
                options_text += f"{option_letters[i]}. {option}\n"
        
        return f"""You are an expert working on a team to answer a multiple choice question.

Here is the question:
{self.question_text}

Here are the options:
{options_text}

Please analyze this question carefully. You must show your reasoning step-by-step.
Your final answer must be in the format: "The answer is X" where X is a single letter (A through J) corresponding to the correct option.
"""

    def get_ground_truth(self) -> str:
        """Return the ground truth answer letter extracted from the answer field."""
        # The answer field might be a letter (A-J) or an index (0-9)
        answer_str = str(self.answer).strip().upper()
        
        # If it's already a letter A-J, return it
        if answer_str in 'ABCDEFGHIJ':
            return answer_str
        
        # If it's a number (index), convert to letter
        try:
            index = int(answer_str)
            if 0 <= index <= 9:
                option_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
                return option_letters[index]
        except ValueError:
            pass
        
        # Fallback: try to extract letter from the answer string
        # Use the base class normalization method
        normalized = self._normalize_answer(answer_str)
        if normalized:
            return normalized
        
        # If all else fails, return the original answer string
        return answer_str

