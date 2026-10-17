import functools
import json
import requests
import os
from datetime import datetime, timezone
import logging
from collections import deque  # for SimpleMemoryCache.order
from langchain_core.messages import BaseMessage  # for type hints in get/set
from typing import Optional

logger = logging.getLogger(__name__)

VISUALIZER_ENDPOINT = os.getenv('VISUALIZER_ENDPOINT', "http://collector:8765/data")

def report_activity(session_id: str, source: str, target: str, content: str, msg_type: str):
    """Sends a standardized message to the visualizer endpoint."""

    if not session_id:
        logging.warning(f"report_activity called with no session_id. Source: {source}, Target: {target}")
        return # Do not send reports without a session ID
    
    data = {"session_id": session_id,"source": source, "target": target, "content": content, "timestamp": datetime.now(timezone.utc).isoformat(), "type": msg_type}
    try:
        requests.post(VISUALIZER_ENDPOINT, json=data, timeout=2)
    except requests.exceptions.RequestException as e:
        logging.warning(f"Could not report activity to visualizer: {e}")


# def report_tool_call(tool_name: str, agent_name: str):
#     """
#     A decorator that reports the execution of a tool to the visualizer.
#     """
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             request_content = { "args": [str(a) for a in args], "kwargs": kwargs }
#             report_activity(
#                 source=agent_name,
#                 target=tool_name,
#                 content=json.dumps(request_content, indent=2),
#                 msg_type="tool_call"
#             )
            
#             result = func(*args, **kwargs)
            
#             report_activity(
#                 source=tool_name,
#                 target=agent_name,
#                 content=str(result),
#                 msg_type="tool_call"
#             )
            
#             return result
#         return wrapper
#     return decorator


# def wrap_tool_for_reporting(tool, agent_name: str):
#     """
#     Takes an Agora Tool object and wraps its execution function (.func)
#     with our reporting logic. This replaces the decorator pattern.
#     Specifically made for Agora, which in its toolformer of functions takes a "snapshot" and thus
#     does not tolerate decorators infront of its tools
#     """
#     original_func = tool.func

#     # functools.wraps is still used to preserve the original function's signature
#     @functools.wraps(original_func)
#     def wrapper(*args, **kwargs):
#         # 1. Report the REQUEST from the agent to the tool
#         request_content = { "args": [str(a) for a in args], "kwargs": kwargs }
#         report_activity(
#             source=agent_name,
#             target=tool.name, # The tool object has a .name attribute
#             content=json.dumps(request_content, indent=2),
#             msg_type="tool_call"
#         )
        
#         # 2. Execute the actual tool function
#         result = original_func(*args, **kwargs)
        
#         # 3. Report the RESPONSE from the tool back to the agent
        
#         report_activity(
#             source=tool.name,
#             target=agent_name,
#             content=str(result),
#             msg_type="tool_call"
#         )
        
#         return result

#     # Replace the tool's original function with our new wrapper
#     tool.func = wrapper
#     return tool

class SimpleMemoryCache:
    """A simple in-memory cache with a maximum size and LRU (Least Recently Used) eviction."""
    def __init__(self, max_size: int = 5000, max_conversation_length: int = 100):
        self.max_size = max_size
        self.max_conversation_length = max_conversation_length
        self.store = {}
        self.order = deque() # Using a deque for efficient appends and pops from both ends

    async def get(self, key: str) -> list[BaseMessage]:
        """Retrieves a conversation history by key."""
        return self.store.get(key, [])

    async def set(self, key: str, value: list[BaseMessage]):
        """Sets a conversation history and manages cache size."""
        # Trim the conversation history if it exceeds the maximum length
        if len(value) > self.max_conversation_length:
            value = value[-self.max_conversation_length:]
            logger.info(f"Trimmed conversation history for key: {key} to {self.max_conversation_length} messages.")

        # Update the store
        self.store[key] = value

        # Update the order, moving key to the front to mark as most recently used
        if key in self.order:
            self.order.remove(key)
        self.order.append(key)

        # Evict oldest item if the cache is at capacity
        if len(self.order) > self.max_size:
            oldest_key = self.order.popleft()
            del self.store[oldest_key]
            logger.info(f"Evicted oldest conversation history for key: {oldest_key}")