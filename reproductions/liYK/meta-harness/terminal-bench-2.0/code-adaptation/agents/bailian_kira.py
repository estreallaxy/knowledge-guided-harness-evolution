"""Bailian compatibility subclass of the unchanged official KIRA snapshot.

The three overrides retain the historical provider and reasoning-history
adaptation. The canonical baseline file and native run loop are unchanged.
"""
import json
import os
from pathlib import Path

import asyncio
import time
from typing import Any

import litellm
from anthropic_caching import add_anthropic_caching
from agents.baseline_kira import (
    AgentHarness as KiraHarness, ImageReadRequest, ToolCallResponse, TOOLS,
)
from harbor.agents.terminus_2.terminus_2 import Command
from harbor.agents.terminus_2.tmux_session import TmuxSession
from harbor.llms.base import ContextLengthExceededError, LLMResponse, OutputLengthExceededError
from harbor.llms.chat import Chat
from litellm.exceptions import (
    AuthenticationError as LiteLLMAuthenticationError,
    BadRequestError,
    ContextWindowExceededError as LiteLLMContextWindowExceededError,
)
from tenacity import (
    retry, retry_if_exception_type, retry_if_not_exception_type,
    stop_after_attempt, wait_exponential,
)


POLICY = Path(__file__).resolve().parents[2] / 'configs/deepseek-api.json'


class AgentHarness(KiraHarness):
    _preserve_reasoning_content = True
    _policy_path = POLICY

    def __init__(self, *args, **kwargs):
        self._bailian_policy = json.loads(self._policy_path.read_text())
        expected = 'openai/' + self._bailian_policy['model']
        if kwargs.get('model_name', expected) != expected:
            raise ValueError('Model must match the fixed Bailian policy')
        if not os.environ.get('BAILIAN_API_KEY') or not os.environ.get('BAILIAN_OPENAI_COMPATIBLE'):
            raise ValueError('BAILIAN_API_KEY and BAILIAN_OPENAI_COMPATIBLE are required')
        kwargs['model_name'] = expected
        kwargs['api_base'] = os.environ['BAILIAN_OPENAI_COMPATIBLE']
        # Explicit limits avoid old LiteLLM metadata guessing an unknown model.
        # Published model context capacity; no artificial output-token cap.
        kwargs.setdefault('model_info', {
            'max_input_tokens': 1000000,
            'supports_function_calling': True,
            'supports_vision': True,
        })
        # Harbor's auxiliary summary calls use the same provider and time policy.
        os.environ['OPENAI_API_KEY'] = os.environ['BAILIAN_API_KEY']
        kwargs['llm_call_kwargs'] = {
            'timeout': self._bailian_policy['socket_timeout_seconds'],
            'extra_body': {'enable_thinking': self._bailian_policy['enable_thinking']},
        }
        kwargs['reasoning_effort'] = None
        super().__init__(*args, **kwargs)

    async def _with_block_timeout(self, coro, timeout_sec=None):
        # Includes summary calls: the outer 600s guard must not cut thinking short.
        return await super()._with_block_timeout(
            coro, timeout_sec if timeout_sec is not None else self._bailian_policy['socket_timeout_seconds']
        )

    def _provider_completion_kwargs(self, kwargs: dict) -> dict:
        result = dict(kwargs)
        result.pop('reasoning_effort', None)
        result.pop('max_tokens', None)
        result.update({
            'api_key': os.environ['BAILIAN_API_KEY'],
            'api_base': os.environ['BAILIAN_OPENAI_COMPATIBLE'],
            'timeout': self._bailian_policy['socket_timeout_seconds'],
            'drop_params': False,
            'extra_body': {
                'enable_thinking': self._bailian_policy['enable_thinking'],
            },
        })
        if result.get('temperature') is None:
            result.pop('temperature', None)
        return result


    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=(
            retry_if_exception_type(Exception)
            & retry_if_not_exception_type(
                (
                    BadRequestError,
                    LiteLLMAuthenticationError,
                    ContextLengthExceededError,
                    OutputLengthExceededError,
                    asyncio.CancelledError,
                )
            )
        ),
        reraise=True,
    )
    async def _call_llm_for_image(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> object:
        """Call litellm.acompletion with retry for transient errors.

        Retries on rate limit, network, and server errors.
        Does NOT retry on BadRequestError (e.g. image too large).
        """
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": 900,  # 15 minutes timeout, retry on timeout
            "drop_params": True,
        }
        # Image analysis doesn't need high reasoning effort
        # Skip reasoning_effort to use default (faster response)
        return await litellm.acompletion(**self._provider_completion_kwargs(kwargs))


    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=(
            retry_if_exception_type(Exception)
            & retry_if_not_exception_type(
                (
                    BadRequestError,
                    LiteLLMAuthenticationError,
                    ContextLengthExceededError,
                    OutputLengthExceededError,
                    asyncio.CancelledError,
                )
            )
        ),
        reraise=True,
    )
    async def _call_llm_with_tools(
        self,
        messages: list[dict],
    ) -> ToolCallResponse:
        """Call LLM directly with tools parameter.

        This bypasses harbor's Chat class to get access to tool_calls.
        """
        # Apply Anthropic caching
        messages = add_anthropic_caching(messages, self._model_name)

        # Build completion kwargs
        completion_kwargs = {
            "model": self._model_name,
            "messages": messages,
            "temperature": self._temperature,
            "tools": TOOLS,
            "timeout": 900,  # 15 minutes timeout, retry on timeout
            "drop_params": True,
        }

        # Add api_base if available
        if hasattr(self._llm, "_api_base") and self._llm._api_base:
            completion_kwargs["api_base"] = self._llm._api_base

        # Add reasoning effort if available
        # When reasoning_effort is set, temperature MUST be 1 (API requirement)
        if self._reasoning_effort:
            completion_kwargs["reasoning_effort"] = self._reasoning_effort
            completion_kwargs["temperature"] = 1

        try:
            response = await litellm.acompletion(
                **self._provider_completion_kwargs(completion_kwargs)
            )
        except LiteLLMContextWindowExceededError:
            raise ContextLengthExceededError()

        # Extract response data
        message = response.choices[0].message
        content = message.content or ""
        tool_calls = self._extract_tool_calls(response)
        usage_info = self._extract_usage_info(response)

        # Check for truncation
        finish_reason = response.choices[0].finish_reason
        if finish_reason == "length":
            raise OutputLengthExceededError(
                "Response was truncated due to max tokens limit",
                truncated_response=content,
            )

        # Extract reasoning content (for models that support it)
        reasoning_content = None
        if hasattr(message, "reasoning_content"):
            reasoning_content = message.reasoning_content

        return ToolCallResponse(
            content=content,
            tool_calls=tool_calls,
            reasoning_content=reasoning_content,
            usage=usage_info,
        )


    async def _handle_llm_interaction(
        self,
        chat: Chat,
        prompt: str,
        original_instruction: str = "",
        session: TmuxSession | None = None,
    ) -> tuple[
        list[Command], bool, str, str, str, LLMResponse, ImageReadRequest | None
    ]:
        """Handle LLM interaction using native tool calling.

        This overrides the parent's _handle_llm_interaction to use native tools
        instead of JSON/XML parsing.
        """
        # Build messages from chat history + new prompt
        messages = chat.messages.copy()
        messages.append({"role": "user", "content": prompt})

        try:
            start_time = time.time()
            tool_response = await self._call_llm_with_tools(messages)
            end_time = time.time()
            request_time_ms = (end_time - start_time) * 1000
            self._api_request_times.append(request_time_ms)

            # Update chat history
            assistant_message = {"role": "assistant", "content": tool_response.content}
            if getattr(self, "_preserve_reasoning_content", False) and tool_response.reasoning_content:
                assistant_message["reasoning_content"] = tool_response.reasoning_content
            if tool_response.tool_calls:
                assistant_message["tool_calls"] = tool_response.tool_calls

            chat._messages.append({"role": "user", "content": prompt})
            chat._messages.append(assistant_message)

            # Add tool result messages for each tool call (required by OpenAI API)
            if tool_response.tool_calls:
                for tc in tool_response.tool_calls:
                    tool_call_id = tc.get("id", "")
                    chat._messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": "executed",
                        }
                    )
                chat.reset_response_chain()

            # Update cumulative metrics
            if tool_response.usage:
                chat._cumulative_input_tokens += tool_response.usage.prompt_tokens
                chat._cumulative_output_tokens += tool_response.usage.completion_tokens
                chat._cumulative_cache_tokens += tool_response.usage.cache_tokens
                chat._cumulative_cost += tool_response.usage.cost_usd

        except ContextLengthExceededError:
            if not self._enable_summarize:
                self.logger.debug("Context length exceeded and summarization is OFF.")
                raise

            self.logger.debug("Context length exceeded. Using fallback summarization.")

            if session is None:
                raise RuntimeError("Cannot handle context length error without session")

            self._unwind_messages_to_free_tokens(chat, target_free_tokens=4000)

            summary_prompt = None
            try:
                summary_prompt, subagent_refs = await self._with_block_timeout(
                    self._summarize(chat, original_instruction, session)
                )
                self._pending_subagent_refs = subagent_refs
                self._pending_handoff_prompt = summary_prompt
            except Exception as e:
                self.logger.debug(f"SUMMARIZATION failed: {e}")

            if summary_prompt is None:
                current_screen = await self._with_block_timeout(
                    session.capture_pane(capture_entire=False)
                )
                limited_screen = current_screen[-1000:] if current_screen else ""
                summary_prompt = (
                    f"{original_instruction}\n\nCurrent state: {limited_screen}"
                )

            # Retry with summarized context
            messages = chat.messages.copy()
            messages.append({"role": "user", "content": summary_prompt})

            start_time = time.time()
            tool_response = await self._call_llm_with_tools(messages)
            end_time = time.time()
            request_time_ms = (end_time - start_time) * 1000
            self._api_request_times.append(request_time_ms)

            # Update chat history
            assistant_message = {"role": "assistant", "content": tool_response.content}
            if getattr(self, "_preserve_reasoning_content", False) and tool_response.reasoning_content:
                assistant_message["reasoning_content"] = tool_response.reasoning_content
            if tool_response.tool_calls:
                assistant_message["tool_calls"] = tool_response.tool_calls

            chat._messages.append({"role": "user", "content": summary_prompt})
            chat._messages.append(assistant_message)

            # Add tool result messages for each tool call
            if tool_response.tool_calls:
                for tc in tool_response.tool_calls:
                    tool_call_id = tc.get("id", "")
                    chat._messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": "executed",
                        }
                    )
                chat.reset_response_chain()

            # Update cumulative metrics
            if tool_response.usage:
                chat._cumulative_input_tokens += tool_response.usage.prompt_tokens
                chat._cumulative_output_tokens += tool_response.usage.completion_tokens
                chat._cumulative_cache_tokens += tool_response.usage.cache_tokens
                chat._cumulative_cost += tool_response.usage.cost_usd

        except OutputLengthExceededError as e:
            self.logger.debug(f"Output length exceeded: {e}")

            error_msg = (
                "ERROR!! Your response was truncated. "
                "Please provide a shorter response with fewer commands."
            )

            chat._messages.extend(
                [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": "[truncated]"},
                    {"role": "user", "content": error_msg},
                ]
            )
            chat.reset_response_chain()

            # Retry
            messages = chat.messages.copy()
            start_time = time.time()
            tool_response = await self._call_llm_with_tools(messages)
            end_time = time.time()
            self._api_request_times.append((end_time - start_time) * 1000)

            assistant_message = {"role": "assistant", "content": tool_response.content}
            if tool_response.tool_calls:
                assistant_message["tool_calls"] = tool_response.tool_calls
            chat._messages.append(assistant_message)

            # Add tool result messages for each tool call
            if tool_response.tool_calls:
                for tc in tool_response.tool_calls:
                    tool_call_id = tc.get("id", "")
                    chat._messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": "executed",
                        }
                    )
                chat.reset_response_chain()

            # Update cumulative metrics
            if tool_response.usage:
                chat._cumulative_input_tokens += tool_response.usage.prompt_tokens
                chat._cumulative_output_tokens += tool_response.usage.completion_tokens
                chat._cumulative_cache_tokens += tool_response.usage.cache_tokens
                chat._cumulative_cost += tool_response.usage.cost_usd

        # Parse tool calls into commands
        commands, is_task_complete, feedback, analysis, plan, image_read = (
            self._parse_tool_calls(tool_response.tool_calls)
        )

        # Create LLMResponse for compatibility with parent class
        llm_response = LLMResponse(
            content=tool_response.content or "",
            reasoning_content=tool_response.reasoning_content,
            usage=tool_response.usage,
        )

        return (
            commands,
            is_task_complete,
            feedback,
            analysis,
            plan,
            llm_response,
            image_read,
        )
