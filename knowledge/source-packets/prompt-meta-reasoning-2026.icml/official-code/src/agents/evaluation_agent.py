"""
Evaluation agent for comparing prompts and providing feedback
"""

from typing import Dict, Union
from .base_agent import BaseAgent
import json


class EvaluationAgent(BaseAgent):
    """Agent responsible for evaluating and comparing prompts"""

    def execute(self, prompt_1: str, prompt_2: str,
                latest_example: str = "", latest_knowledge: str = "") -> Dict:
        """
        Compare two prompts by executing them and evaluating their outputs

        Args:
            prompt_1: First prompt to compare
            prompt_2: Second prompt to compare
            latest_example: Latest example entry
            latest_knowledge: Latest knowledge entry

        Returns:
            Dict containing winner, criteria_used, justification, and feedback
        """
        self.log_info("Starting prompt comparison and evaluation")
        self.log_info(f"latest_example{latest_example}")

        test_question, reference_answer, rationale, skills = self._parse_example_json(latest_example)

        self.log_info(f"Executing prompt 1 on test input: {test_question[:100]}...")
        output_1 = self.call_llm(test_question, system_prompt=prompt_1)

        self.log_info(f"Executing prompt 2 on test input: {test_question[:100]}...")
        output_2 = self.call_llm(test_question, system_prompt=prompt_2)

        criteria = self._parse_knowledge_json(latest_knowledge)

        user_message = self.format_user_message(
            question=test_question,
            answer=reference_answer,
            rationale=rationale,
            skills=skills,
            prompt_1=prompt_1,
            output_1=output_1,
            prompt_2=prompt_2,
            output_2=output_2,
            criteria=criteria
        )

        response = self.call_llm(user_message)

        try:
            evaluation_result = json.loads(response.strip())
            self.log_info(f"Evaluation completed, winner: {evaluation_result['winner']}")
        except (json.JSONDecodeError, Exception) as e:
            self.log_info(f"Failed to parse JSON response: {e}")
            evaluation_result = {"winner": 2}
        return evaluation_result

    def _parse_example_json(self, latest_example):
        """Parse the latest example to extract test data"""

        if isinstance(latest_example, str):
            example_data = json.loads(latest_example)
        elif isinstance(latest_example, dict):
            example_data = latest_example
        else:
            self.log_info(f"Unexpected example type: {type(latest_example)}")
            example_data = {}

        test_question = example_data.get("question", "")
        reference_answer = example_data.get("answer", "")
        rationale = example_data.get("rationale", "")
        skills = ", ".join(example_data.get("tags", ["", ""]))

        return test_question, reference_answer, rationale, skills

    def _parse_knowledge_json(self, latest_knowledge) -> str:
        """Parse knowledge JSON to extract evaluation criteria"""

        if isinstance(latest_knowledge, str):
            knowledge_data = json.loads(latest_knowledge)
        elif isinstance(latest_knowledge, dict):
            knowledge_data = latest_knowledge
        else:
            self.log_info(f"Unexpected knowledge type: {type(latest_knowledge)}")
            knowledge_data = {}

        criteria = "; ".join(knowledge_data.get("evaluation_criteria", ["clarity", "precision"]))

        return criteria
