"""
Example generation agent for creating diverse training examples
"""

import json
import re
from typing import Dict, List
from .base_agent import BaseAgent
import re


class ExampleGenerationAgent(BaseAgent):
    """Agent responsible for generating diverse examples for prompt evaluation"""

    def execute(self, task_description: str, latest_knowledge: str = "",
                recent_examples: str = "", retrieved_information: str = "") -> List[Dict]:
        """
        Generate new examples based on task description and current knowledge

        Args:
            task_description: Description of the task to be performed
            latest_knowledge: Latest knowledge with strategies and principles
            recent_examples: Recent examples for context (to ensure diversity)
            retrieved_information: Information from web search results

        Returns:
            List of example dictionaries
        """
        self.log_info("Starting example generation")

        if isinstance(latest_knowledge, dict):
            knowledge_dict = latest_knowledge
        else:
            try:
                knowledge_dict = json.loads(latest_knowledge) if latest_knowledge else {}
            except:
                knowledge_dict = {}

        user_message = self.format_user_message(
            task_description=task_description,
            strategies=knowledge_dict.get('strategies', []),
            principles=knowledge_dict.get('principles', []),
            evaluation_criteria=knowledge_dict.get('evaluation_criteria', []),
            recent_examples=recent_examples or "No recent examples available",
            retrieved_information=retrieved_information or "No external examples available"
        )

        response = self.call_llm(user_message)
        clean_response = self._clean_llm_json_response(response)

        try:
            example_result = json.loads(clean_response)
            self.log_info(f"Example synthesis completed with one example, having {len(example_result)} fields")
        except json.JSONDecodeError as e:
            self.log_info(f"Failed to parse example JSON: {e}")
            example_result = None
        return example_result


    def _clean_llm_json_response(self, response: str) -> str:
        s = response.strip()
        s = re.sub(r'\\\$', '$', s)         # \$ -> $
        s = re.sub(r'\\%', '%', s)          # \% -> %
        s = re.sub(r"\\_", "_", s)          # \_ -> _
        # Keep only valid JSON escapes
        s = re.sub(
            r'\\(?!["\\/bfnrtu])',
            '', s
        )
        s = re.sub(r',\s*}', '}', s)        # Remove trailing comma in objects
        s = re.sub(r',\s*]', ']', s)        # Remove trailing comma in arrays
        return s
