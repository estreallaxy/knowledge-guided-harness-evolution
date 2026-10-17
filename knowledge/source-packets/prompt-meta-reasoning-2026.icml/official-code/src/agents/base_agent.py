"""
Base agent class
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
import re

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all MR.PEA cognitive agents"""

    # Class-level token tracking (shared across all agents)
    _total_input_tokens = 0
    _total_output_tokens = 0
    _total_api_calls = 0

    def __init__(self, system_prompt: Dict, user_message: Dict, openai_client, config: Dict):
        """
        Initialize base agent with simplified parameters

        Args:
            system_prompt: Agent-specific system prompt configuration
            user_prompts: Agent-specific user prompt templates
            openai_client: OpenAI client for API calls
            config: Agent-specific configuration (temperature, model, max_tokens)
        """
        self.system_prompt_config = system_prompt
        self.user_message = user_message
        self.openai_client = openai_client
        self.config = config

        self.agent_name = self.__class__.__name__

        # Get system prompt text and user message template
        self.system_prompt = self.system_prompt_config.get('system_prompt', '')
        self.user_message_template = self.user_message.get('template', '')

        # Extract agent-specific settings from config
        self.temperature = self.config.get('temperature', 0.5)
        self.model = self.config.get('model', 'gpt-4o-mini')
        self.max_tokens = self.config.get('max_tokens', 2048)

        logger.info(f"Initialized {self.agent_name} agent")
        logger.info(f"[{self.agent_name}] Configuration - Model: {self.model}, Temperature: {self.temperature}, Max tokens: {self.max_tokens}")

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function"""
        pass

    def call_llm(self, user_message: str, **kwargs) -> str:
        """Call LLM with agent-specific configuration and log token usage"""
        try:
            system_prompt = kwargs.get('system_prompt', self.system_prompt)

            self.log_info(f"Making LLM call with model: {self.model}")
            self.log_debug(f"System prompt length: {len(system_prompt)} characters")
            self.log_debug(f"User message length: {len(user_message)} characters")

            response= self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            response_text = response.choices[0].message.content

            json_blocks = re.findall(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
            if json_blocks:
                response_text = json_blocks[0].strip()
            else:
                response_text=response_text.strip()
            self._log_llm_execution(response, system_prompt, user_message, response_text)
            return response_text

        except Exception as e:
            logger.error(f"LLM API call failed for {self.agent_name}: {e}")
            logger.error(f"System prompt: {system_prompt[:200]}...")
            logger.error(f"User message: {user_message[:200]}...")
            raise RuntimeError(f"Failed to call OpenAI API for {self.agent_name}: {e}")

    def _log_llm_execution(self, response,  system_prompt: str, user_message: str, return_message: str):
        BaseAgent._total_api_calls += 1
        BaseAgent._total_input_tokens += response.usage.prompt_tokens
        BaseAgent._total_output_tokens += response.usage.completion_tokens

        logger.info(f"[LLM][{self.agent_name}] Model: {self.model}, Temperature: {self.temperature}, Max tokens: {self.max_tokens}")
        logger.info(f"[LLM][{self.agent_name}] SYSTEM PROMPT: {system_prompt}")
        logger.info(f"[LLM][{self.agent_name}] USER MESSAGE: {user_message}")
        logger.info(f"[LLM][{self.agent_name}] RESPONSE: {return_message}")

    def _format_list_items(self, items: list, prefix: str = "- ") -> str:
        """Format a list of items as a string with prefixes"""
        if not items:
            return ""
        return "\n".join([f"{prefix}{item}" for item in items])

    def format_user_message(self, **kwargs) -> str:
        """Format the user prompt template with provided variables"""

        template = self.user_message_template

        if not template:
            logger.warning(f"No user prompt template available for agent: {self.agent_name}")
            return ""

        try:
            formatted_template = template
            for key, value in kwargs.items():
                formatted_template = formatted_template.replace('{{' + key + '}}', str(value))
                formatted_template = formatted_template.replace('{' + key + '}', str(value))
            return formatted_template
        except Exception as e:
            logger.error(f"Failed to format template for agent {self.agent_name}: {e}")
            return template

    def log_info(self, message: str):
        """Log information about agent execution"""
        logger.info(f"[{self.agent_name.upper()}] {message}")

    def log_debug(self, message: str):
        """Log debug information about agent execution"""
        logger.debug(f"[{self.agent_name.upper()}] {message}")

    @classmethod
    def get_total_token_usage(cls) -> Dict[str, int]:
        """Get total token usage across all agents"""
        return {
            "total_input_tokens": cls._total_input_tokens,
            "total_output_tokens": cls._total_output_tokens,
            "total_tokens": cls._total_input_tokens + cls._total_output_tokens,
            "total_api_calls": cls._total_api_calls
        }
