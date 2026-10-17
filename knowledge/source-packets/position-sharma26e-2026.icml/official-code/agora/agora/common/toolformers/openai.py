import json
from typing import TYPE_CHECKING, List, Optional
import asyncio

from agora.common.core import Conversation
from agora.common.toolformers.base import Tool, Toolformer, ToolLike

# Standard pattern for optional imports
try:
    import openai
    OPENAI_IMPORT_ERROR = None
except ImportError as e:
    openai = None
    OPENAI_IMPORT_ERROR = e


class OpenAIConversation(Conversation):
    """Handles conversations using an OpenAI-compatible client."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        tools: List[Tool],
        system_prompt: str,
        category: Optional[str] = None,
    ) -> None:
        """Initialize the OpenAIConversation.

        Args:
            api_key (str): The API key for the service.
            base_url (str): The base URL of the OpenAI-compatible API.
            model (str): The name of the model to use.
            tools (List[Tool]): A list of Tool instances available to the model.
            system_prompt (str): The system prompt to guide the conversation.
            category (Optional[str], optional): The category of the conversation. Defaults to None.
        """
        if OPENAI_IMPORT_ERROR:
            raise OPENAI_IMPORT_ERROR

        self.client = openai.Client(api_key=api_key, base_url=base_url)
        self.model = model
        self.tools = {tool.name: tool for tool in tools}
        self.category = category
        self.messages = [{"role": "system", "content": system_prompt}]

    def __call__(self, message: str, print_output: bool = True) -> str:
        """Process a message and handle the full tool-use loop."""
        import logging

        self.messages.append({"role": "user", "content": message})

        while True:
            #logging.debug("--- SENDING TO OPENAI (SYNC) ---")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=[tool.openai_schema for tool in self.tools.values()],
            )
            
            #logging.debug("--- RAW RESPONSE FROM OPENAI ---")
            #logging.debug(f"OPENAI RESPONSE OBJECT: {response}")

            response_message = response.choices[0].message
            # Append the Pydantic model as a dict
            self.messages.append(response_message.model_dump())

            if not response_message.tool_calls:
                # No tool calls, we have our final answer
                final_content = response_message.content or ""
                if print_output:
                    print(final_content)
                return final_content

            # A tool call was made, so we execute it
            tool_calls = response_message.tool_calls
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                
                if function_name not in self.tools:
                    result = f"Error: Tool '{function_name}' not found."
                else:
                    function_to_call = self.tools[function_name].func
                    # OpenAI returns arguments as a JSON *string*, must be loaded
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        result = f"Error: Failed to parse arguments for {function_name}. Invalid JSON: {e}"
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": str(result),
                        })
                        continue

                    if print_output:
                        print(f"Executing tool: {function_name}({function_args})")
                        
                    try:
                        # Preserve your logic of running async tools in a sync loop
                        if asyncio.iscoroutinefunction(function_to_call):
                            result = asyncio.run(function_to_call(**function_args))
                        else:
                            result = function_to_call(**function_args)
                    except Exception as e:
                        result = f"Error executing tool '{function_name}': {e}"
                
                # Append the tool result in the format OpenAI expects
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(result),
                })
        
class OpenAIToolformer(Toolformer):
    """Toolformer implementation using an OpenAI-compatible client."""

    def __init__(self, model: str, api_key: str, base_url: str) -> None:
        """Initialize the OpenAIToolformer.

        Args:
            model (str): The name of the model to use.
            api_key (str): The API key.
            base_url (str): The API base URL.
        
        Raises:
            ImportError: If the 'openai' library is not installed.
        """
        if OPENAI_IMPORT_ERROR:
            raise OPENAI_IMPORT_ERROR
            
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def new_conversation(
        self, prompt: str, tools: List[ToolLike], category: Optional[str] = None
    ) -> Conversation:
        """Start a new conversation with the given prompt and tools."""
        
        # Ensure all provided tools are proper Tool instances
        processed_tools = [Tool.from_toollike(tool) for tool in tools]
        
        return OpenAIConversation(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            tools=processed_tools,
            system_prompt=prompt,
            category=category,
        )