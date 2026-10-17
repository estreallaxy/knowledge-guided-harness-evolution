import copy
import json
from typing import Dict, Iterator, List, Literal, Optional, Union

from openai import OpenAI

from qwen_agent import Agent
from qwen_agent.llm.schema import CONTENT, DEFAULT_SYSTEM_MESSAGE, ROLE, SYSTEM, ContentItem, Message, FUNCTION
from qwen_agent.tools import BaseTool
from qwen_agent.memory import Memory
from qwen_agent.log import logger
from qwen_agent.utils.utils import extract_files_from_messages, get_basename_from_url, print_traceback
from config import MAX_LLM_CALL_PER_RUN


class SocialMediaAgent(Agent):
    def __init__(self,
                 llm: Optional[dict],
                 function_list: Optional[List[Union[str, Dict, BaseTool]]] = None,
                 system_message: Optional[str] = '',
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 files: Optional[List[str]] = None,
                 **kwargs):
        """Initialization the agent.

        Args:
            function_list: One list of tool name, tool configuration or Tool object,
              such as 'code_interpreter', {'name': 'code_interpreter', 'timeout': 10}, or CodeInterpreter().
            system_message: The specified system message for LLM chat.
            name: The name of this agent.
            description: The description of this agent, which will be used for multi_agent.
        """
        super().__init__(function_list=function_list,
                         llm=llm,
                         system_message=system_message,
                         name=name,
                         description=description)

        #self.memory = ""
        self.mem = Memory(llm=llm, files=files, **kwargs)
        #self.folder = {}
        
    def _run(self, messages: List[Message], lang: Literal['en', 'zh'] = 'zh', **kwargs) -> Iterator[List[Message]]:
        messages = copy.deepcopy(messages)
        num_llm_calls_available = MAX_LLM_CALL_PER_RUN
        response = []
        while True and num_llm_calls_available > 0:
            num_llm_calls_available -= 1

            output = self._call_llm(messages=messages, 
                                    functions=[func.function for func in self.function_map.values()], 
                                    stream=False)

            if output:
                response.extend(output)
                messages.extend(output)
                yield response
                used_any_tool = False
                for out in output:
                    for use_tool, tool_name, tool_args, _ in self._detect_tool(out):
                        if use_tool:
                            tool_result = self._call_tool(tool_name, tool_args, messages=messages, **kwargs)
                            fn_msg = Message(
                                role=FUNCTION,
                                name=tool_name,
                                content=tool_result,
                            )
                            messages.append(fn_msg)
                            response.append(fn_msg)
                            yield response
                            used_any_tool = True
                if not used_any_tool:
                    break
        yield response

    def _call_tool(self, tool_name: str, tool_args: Union[str, dict] = '{}', **kwargs) -> str:
        if tool_name not in self.function_map:
            return f'Tool {tool_name} does not exists.'
        # Temporary plan: Check if it is necessary to transfer files to the tool
        # Todo: This should be changed to parameter passing, and the file URL should be determined by the model
        if "data_folder" in self.function_map:
            kwargs["data_folder"] = self.function_map["data_folder"]
        if self.function_map[tool_name].file_access:
            assert 'messages' in kwargs
            files = extract_files_from_messages(kwargs['messages'], include_images=True) + self.mem.system_files
            return super()._call_tool(tool_name, tool_args, files=files, **kwargs)
        else:
            return super()._call_tool(tool_name, tool_args, **kwargs)
        