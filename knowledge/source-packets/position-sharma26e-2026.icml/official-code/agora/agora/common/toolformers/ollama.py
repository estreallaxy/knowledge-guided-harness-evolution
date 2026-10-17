import json
from typing import TYPE_CHECKING, List, Optional
import asyncio

from agora.common.core import Conversation
from agora.common.toolformers.base import Tool, Toolformer, ToolLike

# Standard pattern for optional imports
try:
    import ollama
    OLLAMA_IMPORT_ERROR = None
except ImportError as e:
    ollama = None
    OLLAMA_IMPORT_ERROR = e


class OllamaConversation(Conversation):
    """Handles conversations using a direct Ollama client."""

    def __init__(
        self,
        host: str,
        model: str,
        tools: List[Tool],
        system_prompt: str,
        category: Optional[str] = None,
    ) -> None:
        """Initialize the OllamaConversation.

        Args:
            host (ollama.AsyncClient): An initialized Ollama async client.
            model (str): The name of the Ollama model to use (e.g., "llama3").
            tools (List[Tool]): A list of Tool instances available to the model.
            system_prompt (str): The system prompt to guide the conversation.
            category (Optional[str], optional): The category of the conversation. Defaults to None.
        """
        if OLLAMA_IMPORT_ERROR:
            raise OLLAMA_IMPORT_ERROR

        self.client = ollama.Client(host=host)
        self.model = model
        self.tools = {tool.name: tool for tool in tools}
        self.category = category
        self.messages = [{"role": "system", "content": system_prompt}]

    def __call__(self, message: str, print_output: bool = True) -> str:
        """Process a message and handle the full tool-use loop.

        Args:
            message (str): The message to process.
            print_output (bool, optional): Whether to print intermediate and final outputs. Defaults to True.

        Returns:
            str: The final text response from the conversation.
        """
        import logging

        self.messages.append({"role": "user", "content": message})

        while True:
            #logging.debug("--- SENDING TO OLLAMA (SYNC) ---")
            
            # Use the synchronous client's chat method
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=[tool.openai_schema for tool in self.tools.values()],
            )
            
            #logging.debug("--- RAW RESPONSE FROM OLLAMA ---")
            #logging.debug(f"OLLAMA RESPONSE OBJECT: {response}")

            response_message = response["message"]
            self.messages.append(response_message)

            if not response_message.get("tool_calls"):
                # No tool calls, we have our final answer
                final_content = response_message.get("content", "")
                if print_output:
                    print(final_content)
                return final_content

            # A tool call was made, so we execute it
            tool_calls = response_message["tool_calls"]
            
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                
                if function_name not in self.tools:
                    result = f"Error: Tool '{function_name}' not found."
                else:
                    function_to_call = self.tools[function_name].func
                    function_args = tool_call["function"]["arguments"]
                    
                    if print_output:
                        print(f"Executing tool: {function_name}({function_args})")
                        
                    try:
                        # Since the tool itself might be async (like our talk_to_peer),
                        # we must run it in a new loop here. This is safe because the top-level
                        # loop from guesser_client isn't being accessed.
                        if asyncio.iscoroutinefunction(function_to_call):
                            result = asyncio.run(function_to_call(**function_args))
                        else:
                            result = function_to_call(**function_args)
                    except Exception as e:
                        result = f"Error executing tool '{function_name}': {e}"
                
                self.messages.append({
                    "role": "tool",
                    "content": str(result),
                })
        
class OllamaToolformer(Toolformer):
    """Toolformer implementation using a direct Ollama client."""

    def __init__(self, model: str, host: Optional[str] = None) -> None:
        """Initialize the OllamaToolformer.

        Args:
            model (str): The name of the Ollama model to use (e.g., "llama3").
            host (Optional[str], optional): The URL of the Ollama host. Defaults to env var or localhost.
        
        Raises:
            ImportError: If the 'ollama' library is not installed.
        """
        if OLLAMA_IMPORT_ERROR:
            raise OLLAMA_IMPORT_ERROR
            
        self.model = model
        self.host = host

    def new_conversation(
        self, prompt: str, tools: List[ToolLike], category: Optional[str] = None
    ) -> Conversation:
        """Start a new conversation with the given prompt and tools.

        Args:
            prompt (str): The initial prompt for the conversation.
            tools (List[ToolLike]): A list of tools to be available in the conversation.
            category (Optional[str], optional): The category of the conversation. Defaults to None.

        Returns:
            OllamaConversation: A Conversation instance managing the interaction.
        """
        
        # Ensure all provided tools are proper Tool instances
        processed_tools = [Tool.from_toollike(tool) for tool in tools]
        
        return OllamaConversation(
            host=self.host,
            model=self.model,
            tools=processed_tools,
            system_prompt=prompt,
            category=category,
        )