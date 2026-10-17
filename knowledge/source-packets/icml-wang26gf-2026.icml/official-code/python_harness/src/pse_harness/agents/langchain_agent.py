"""LangChain-based agent implementation."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Optional, Sequence
from uuid import uuid4

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import BaseTool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import structlog

from .base import (
    AgentConfig,
    AgentResponse,
    AgentStatus,
    AgentStep,
    BaseAgent,
    Tool,
    ToolCall,
)

logger = structlog.get_logger()


def convert_to_langchain_tool(tool: Tool) -> BaseTool:
    """Convert our Tool to a LangChain tool."""
    def wrapper(**kwargs):
        if tool.handler:
            return tool.handler(**kwargs)
        return f"Tool {tool.name} has no handler"

    return StructuredTool.from_function(
        func=wrapper,
        name=tool.name,
        description=tool.description,
        args_schema=None,
    )


class LangChainAgent(BaseAgent):
    """Agent using LangChain framework with direct tool calling."""

    def __init__(
        self,
        config: AgentConfig,
        tools: Optional[list[Tool]] = None,
        api_key: Optional[str] = None,
    ):
        super().__init__(config, tools)

        # Initialize LLM based on provider
        if config.model_provider == "openai":
            self.llm = ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=api_key,
            )
        elif config.model_provider == "anthropic":
            self.llm = ChatAnthropic(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=api_key,
            )
        else:
            raise ValueError(f"Unsupported provider: {config.model_provider}")

        self._system_prompt = "You are a helpful assistant."
        self._langchain_tools: list[BaseTool] = []
        self._message_history: list[BaseMessage] = []

        # Convert and bind tools
        self._update_langchain_tools()

    def _update_langchain_tools(self) -> None:
        """Update LangChain tools from our tool definitions."""
        self._langchain_tools = [convert_to_langchain_tool(t) for t in self.tools]
        if self._langchain_tools:
            self._llm_with_tools = self.llm.bind_tools(self._langchain_tools)
        else:
            self._llm_with_tools = self.llm

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt."""
        self._system_prompt = prompt

    def register_tool(self, tool: Tool) -> None:
        """Register a new tool."""
        super().register_tool(tool)
        self._update_langchain_tools()

    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self._message_history = []

    async def run(self, task: str) -> AgentResponse:
        """Run the agent on a task."""
        run_id = uuid4()
        start_time = datetime.utcnow()
        steps = []
        tool_call_sequence = []
        total_tokens = 0
        status = AgentStatus.RUNNING
        final_output = ""

        logger.info(
            "LangChain agent run started",
            run_id=str(run_id),
            task=task[:100],
            agent_id=self.config.agent_id,
        )

        try:
            messages = [SystemMessage(content=self._system_prompt)]
            messages.extend(self._message_history)
            messages.append(HumanMessage(content=task))

            for step_num in range(self.config.max_steps):
                response = await self._llm_with_tools.ainvoke(messages)

                # Check for tool calls
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    messages.append(response)
                    step_tool_calls = []

                    for tc in response.tool_calls:
                        tool_call = ToolCall(
                            id=uuid4(),
                            name=tc['name'],
                            arguments=tc.get('args', {}),
                        )

                        # Execute tool
                        try:
                            result = self.execute_tool(tc['name'], tc.get('args', {}))
                            tool_call.result = result
                        except Exception as e:
                            tool_call.error = str(e)
                            result = f"Error: {e}"

                        step_tool_calls.append(tool_call)
                        tool_call_sequence.append(tc['name'])

                        # Add tool result to messages
                        from langchain_core.messages import ToolMessage
                        messages.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tc['id'],
                        ))

                    steps.append(AgentStep(
                        step_num=step_num,
                        input=task if step_num == 0 else "",
                        output=response.content or "",
                        tool_calls=step_tool_calls,
                    ))
                else:
                    # No tool calls - final response
                    final_output = response.content or ""
                    steps.append(AgentStep(
                        step_num=step_num,
                        input=task if step_num == 0 else "",
                        output=final_output,
                        tool_calls=[],
                    ))
                    status = AgentStatus.SUCCESS
                    break
            else:
                status = AgentStatus.TIMEOUT

            # Update message history
            self._message_history.append(HumanMessage(content=task))
            self._message_history.append(AIMessage(content=final_output))

        except Exception as e:
            status = AgentStatus.FAILED
            logger.error("LangChain agent run failed", run_id=str(run_id), error=str(e))

            return AgentResponse(
                run_id=run_id,
                status=status,
                final_output="",
                steps=steps,
                tool_call_sequence=tool_call_sequence,
                total_tokens=total_tokens,
                total_duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                error=str(e),
            )

        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        response = AgentResponse(
            run_id=run_id,
            status=status,
            final_output=final_output,
            steps=steps,
            tool_call_sequence=tool_call_sequence,
            total_tokens=total_tokens,
            total_duration_ms=duration_ms,
        )

        self._run_history.append(response)

        logger.info(
            "LangChain agent run completed",
            run_id=str(run_id),
            status=status.value,
            num_steps=len(steps),
            duration_ms=duration_ms,
        )

        return response

    async def step(self, input_text: str) -> AgentStep:
        """Execute a single interactive step."""
        response = await self.run(input_text)
        return response.steps[-1] if response.steps else AgentStep(
            step_num=0,
            input=input_text,
            output="",
            tool_calls=[],
        )
