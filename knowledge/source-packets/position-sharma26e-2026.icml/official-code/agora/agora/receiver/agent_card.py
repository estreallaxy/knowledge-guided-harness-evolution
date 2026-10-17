from typing import List, Optional
from agora.common.toolformers.base import Tool

class AgentCard:
    """
    A standalone class to generate a self-describing manifest for an agent.
    """
    def __init__(
        self,
        name: str,
        description: str,
        tools: List[Tool],
        version: str = "1.0.0",
        url: Optional[str] = None,
        protocol_version: str = "agora-custom-http-0.1",
        default_input_modes: List[str] = None,
        default_output_modes: List[str] = None,
    ):
        self.name = name
        self.description = description
        self.tools = tools
        self.version = version
        self.configured_url = url
        self.protocol_version = protocol_version
        self.default_input_modes = default_input_modes or ["text/plain", "application/json"]
        self.default_output_modes = default_output_modes or ["text/plain"]

    def generate(self, base_url: str) -> dict:
        """
        Dynamically generates the agent's self-description card as a dictionary.

        Args:
            base_url (str): The base URL of the running server, determined at request time.
        
        Returns:
            dict: The agent card manifest.
        """
        final_url = self.configured_url or request_base_url
        skills = []
        for tool in self.tools:
            skill = {
                "skill_name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema,
                "returns": tool.return_schema
            }
            skills.append(skill)

        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "url": base_url,
            "protocol_version": self.protocol_version,
            "default_input_modes": self.default_input_modes,
            "default_output_modes": self.default_output_modes,
            "capabilities": {
                "tool_calling": True
            },
            "skills": skills,
            "additional_interfaces": [
                {
                    "url": f"{final_url}/messages",
                    "transport": "HTTP-POST",
                    "description": "Main endpoint for all agent skills. Message in body, metadata in cookies."
                }
            ]
        }