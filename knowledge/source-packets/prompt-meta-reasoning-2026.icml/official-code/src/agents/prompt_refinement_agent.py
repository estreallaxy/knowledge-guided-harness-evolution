"""
Prompt refinement agent for refining existing prompts based on knowledge and feedbackRefines existing prompts based on knowledge and feedback
"""

import json
from typing import Dict
from .base_agent import BaseAgent


class PromptRefinementAgent(BaseAgent):
    """Agent responsible for refining and improving prompts"""

    def execute(self, current_best: str, task_description: str, latest_knowledge: str = "",
                latest_example: str = "", latest_feedback: str = "", historical_prompts_with_scores: str = "",
                retrieved_information: str = "") -> str:
        """
        Refine existing prompt based on knowledge and feedback

        Args:
            current_best: Current best prompt to be refined
            latest_knowledge: Latest knowledge entry
            latest_example: Latest example entry
            latest_feedback: Latest feedback from previous evaluations
            historical_prompts_with_scores: Top historical prompts with their scores
            retrieved_information: Retrieved information from web search

        Returns:
            Refined prompt string
        """
        self.log_info("Refining prompt based on feedback and knowledge")

        user_message = self.format_user_message(
            current_best=current_best,
            task_description=task_description,
            latest_example=self._clean_example_for_input(latest_example),
            latest_strategies=latest_knowledge.get("strategies", []),
            latest_principles=latest_knowledge.get("principles", []),
            latest_criteria=latest_knowledge.get("evaluation_criteria", []),
            latest_feedback=latest_feedback or "No previous feedback available",
            historical_prompts_with_scores=historical_prompts_with_scores or "No historical prompts available",
            retrieved_information=retrieved_information or "No retrieved information available"
        )

        response = self.call_llm(user_message)

        try:
            parsed_response = json.loads(response.strip())
            refined_prompt = parsed_response.get("new_prompt", response.strip())
            self.log_info("Prompt refinement completed successfully")
            return refined_prompt
        except json.JSONDecodeError as e:
            self.log_info(f"Failed to parse JSON response: {e}, using raw response")
            return response.strip()

    def _clean_example_for_input(self, latest_example: str) -> str:

        if not latest_example:
            return latest_example

        try:
            if isinstance(latest_example, str):
                knowledge_dict = json.loads(latest_example)
            else:
                knowledge_dict = latest_example

            cleaned_dict = {k: v for k, v in knowledge_dict.items()
                            if k not in ['variation_type']}

            return json.dumps(cleaned_dict, ensure_ascii=False)

        except (json.JSONDecodeError, TypeError):
            return latest_example
