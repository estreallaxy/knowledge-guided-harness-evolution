"""OpenAI-based agent implementation."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from openai import AsyncOpenAI
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


class OpenAIAgent(BaseAgent):
    """Agent using OpenAI's API directly."""

    def __init__(
        self,
        config: AgentConfig,
        tools: Optional[list[Tool]] = None,
        api_key: Optional[str] = None,
    ):
        super().__init__(config, tools)
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._messages: list[dict] = []
        self._system_prompt = ""

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt."""
        self._system_prompt = prompt

    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self._messages = []

    async def run(self, task: str) -> AgentResponse:
        """Run the agent on a task."""
        run_id = uuid4()
        start_time = datetime.utcnow()
        steps = []
        tool_call_sequence = []
        total_tokens = 0
        status = AgentStatus.RUNNING

        logger.info(
            "Agent run started",
            run_id=str(run_id),
            task=task[:100],
            agent_id=self.config.agent_id,
        )

        # Initialize messages
        self._messages = []
        if self._system_prompt:
            self._messages.append({"role": "system", "content": self._system_prompt})
        self._messages.append({"role": "user", "content": task})

        try:
            for step_num in range(self.config.max_steps):
                step = await self._execute_step(step_num, task if step_num == 0 else "")
                steps.append(step)
                total_tokens += sum(step.token_usage.values())

                # Track tool calls
                for tc in step.tool_calls:
                    tool_call_sequence.append(tc.name)

                # Check if done (no tool calls in response)
                if not step.tool_calls:
                    status = AgentStatus.SUCCESS
                    break

            if status != AgentStatus.SUCCESS:
                status = AgentStatus.TIMEOUT
                logger.warning("Agent reached max steps", run_id=str(run_id))

        except Exception as e:
            status = AgentStatus.FAILED
            logger.error("Agent run failed", run_id=str(run_id), error=str(e))

            response = AgentResponse(
                run_id=run_id,
                status=status,
                final_output="",
                steps=steps,
                tool_call_sequence=tool_call_sequence,
                total_tokens=total_tokens,
                total_duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                error=str(e),
            )
            self._run_history.append(response)
            return response

        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        final_output = steps[-1].output if steps else ""

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
            "Agent run completed",
            run_id=str(run_id),
            status=status.value,
            num_steps=len(steps),
            total_tokens=total_tokens,
            duration_ms=duration_ms,
        )

        return response

    async def _execute_step(self, step_num: int, input_text: str) -> AgentStep:
        """Execute a single step."""
        step_start = datetime.utcnow()

        # Build request
        request_params = {
            "model": self.config.model_name,
            "messages": self._messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        # Add tools if available
        if self.tools:
            request_params["tools"] = [t.to_openai_schema() for t in self.tools]
            request_params["tool_choice"] = "auto"

        # Call API
        response = await self.client.chat.completions.create(**request_params)

        message = response.choices[0].message
        tool_calls_made = []

        # Process tool calls
        if message.tool_calls:
            # Add assistant message to history
            self._messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            # Execute each tool call
            for tc in message.tool_calls:
                tool_start = datetime.utcnow()
                tool_call = ToolCall(
                    id=uuid4(),
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                )

                try:
                    result = self.execute_tool(tc.function.name, tool_call.arguments)
                    tool_call.result = result
                except Exception as e:
                    tool_call.error = str(e)
                    result = f"Error: {e}"

                tool_call.duration_ms = (datetime.utcnow() - tool_start).total_seconds() * 1000
                tool_calls_made.append(tool_call)

                # Add tool result to messages
                self._messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result) if not isinstance(result, str) else result,
                })

                logger.debug(
                    "Tool executed",
                    tool_name=tc.function.name,
                    duration_ms=tool_call.duration_ms,
                )
        else:
            # No tool calls - add response to messages
            self._messages.append({
                "role": "assistant",
                "content": message.content or "",
            })

        step = AgentStep(
            step_num=step_num,
            input=input_text,
            output=message.content or "",
            tool_calls=tool_calls_made,
            thought=None,
            token_usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
        )

        return step

    async def step(self, input_text: str) -> AgentStep:
        """Execute a single interactive step."""
        self._messages.append({"role": "user", "content": input_text})
        return await self._execute_step(len(self._messages), input_text)
