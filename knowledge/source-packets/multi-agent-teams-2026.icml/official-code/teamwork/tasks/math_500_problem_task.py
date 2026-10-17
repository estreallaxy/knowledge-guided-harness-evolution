"""MATH-500 Problem Task implementation."""

from typing import Optional

from teamwork.tasks.collaborative_math_task import CollaborativeMathTask


class Math500ProblemTask(CollaborativeMathTask):
    """Task representing a single problem from the MATH-500 dataset.
    
    This class handles a specific math problem instance, providing the
    problem text and ground truth extraction logic.
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
        llm_fallback_model: str = "gpt-4o",
        llm_fallback_api_key: Optional[str] = None,
    ):
        """Initialize the MATH-500 problem task.

        Args:
            agent_ids: List of participating agent IDs.
            max_rounds: Maximum rounds of collaboration.
            problem_data: Dictionary containing 'problem' and 'solution' from the dataset.
            unique_id: Unique identifier for this problem instance.
            seed: Random seed for this specific task instance.
            decision_mode: Collaboration strategy.
            most_capable_model_name: Fallback expert model name.
            use_llm_fallback: Whether to use LLM as final fallback for equivalence checking.
            llm_fallback_model: Model name for LLM fallback (e.g., "gpt-4o", "gpt-5").
            llm_fallback_api_key: OpenAI API key for LLM fallback.
        """
        super().__init__(
            agent_ids=agent_ids,
            max_rounds=max_rounds,
            seed=seed,
            decision_mode=decision_mode,
            most_capable_model_name=most_capable_model_name,
            name=f"Math500-{unique_id}",
            use_llm_fallback=use_llm_fallback,
            llm_fallback_model=llm_fallback_model,
            llm_fallback_api_key=llm_fallback_api_key,
        )
        
        self.problem_text = problem_data.get('problem', '')
        self.solution_text = problem_data.get('solution', '')
        self.unique_id = unique_id

    def get_task_description(self, agent_id: int) -> str:
        """Return the task description (problem statement) for a specific agent."""
        return f"""You are a mathematician working on a team to solve a complex math problem.

Here is the problem:
{self.problem_text}

Please solve this problem carefully. You must show your reasoning step-by-step.
Your final answer must be a single numerical value or expression wrapped in \\boxed{{}}.
For example: \\boxed{{42}} or \\boxed{{\\frac{{1}}{{2}}}}.
"""

    def get_ground_truth(self) -> str:
        """Return the ground truth answer extracted from the solution text."""
        # Use the base class helper to extract the boxed answer from the reference solution
        return self._extract_answer(self.solution_text)
