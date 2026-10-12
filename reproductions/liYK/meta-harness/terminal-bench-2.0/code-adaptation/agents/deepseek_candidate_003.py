"""DeepSeek KIRA harness with generic tool-argument robustness.

Evidence-driven, task-agnostic fixes on top of agents.deepseek_kira.AgentHarness:

1. Crash-proof tool argument parsing. Training evidence shows the model provider
   sometimes serializes the ``duration`` field of an execute_commands tool call
   as a JSON string; the base parser feeds it straight into min(duration, 60)
   and an unhandled TypeError aborted whole agent runs on their first turn.
   Durations, keystrokes, and command containers are now coerced defensively and
   malformed entries are skipped with a log instead of crashing the episode.

2. reasoning_content preservation in the output-truncation retry path. The
   normal and context-summarization paths store reasoning_content on assistant
   tool-call messages when _preserve_reasoning_content is set; the
   OutputLengthExceededError retry path dropped it, which removed the
   provider-specific reasoning field from a stored message and from the next
   outbound tool continuation. The same preservation gate now applies there.

No prompt, provider, model, thinking, or native time-limit changes are made.
"""
import json
import time
from typing import Any

from agents.baseline_kira import ImageReadRequest
from agents.deepseek_kira import AgentHarness as DeepSeekKiraHarness
from harbor.agents.terminus_2.terminus_2 import Command
from harbor.agents.terminus_2.tmux_session import TmuxSession
from harbor.llms.base import (
    ContextLengthExceededError,
    LLMResponse,
    OutputLengthExceededError,
)
from harbor.llms.chat import Chat

_MAX_COMMAND_DURATION_SEC = 60.0


class AgentHarness(DeepSeekKiraHarness):
    """DeepSeek KIRA with generic tool-argument robustness (no task logic)."""

    @staticmethod
    def _coerce_duration(raw, default: float = 1.0) -> float:
        """Coerce a model-supplied duration into a finite number in [0, 60]."""
        if raw is None:
            return default
        if isinstance(raw, bool):
            value = 1.0 if raw else 0.0
        elif isinstance(raw, (int, float)):
            value = float(raw)
        elif isinstance(raw, str):
            stripped = raw.strip()
            if not stripped:
                return default
            try:
                value = float(stripped)
            except ValueError:
                return default
        else:
            return default
        if value != value:  # NaN
            return default
        return max(0.0, min(_MAX_COMMAND_DURATION_SEC, value))

    def _parse_tool_calls(
        self, tool_calls: list[dict[str, Any]]
    ) -> tuple[list[Command], bool, str, str, str, ImageReadRequest | None]:
        """Parse tool calls defensively; never raise on malformed arguments.

        Mirrors the base parser behavior (including double-encoded commands
        strings) while coercing durations and keystrokes and skipping malformed
        entries instead of letting a TypeError escape the harness.
        """
        commands: list[Command] = []
        is_task_complete = False
        feedback = ""
        analysis = ""
        plan = ""
        image_read = None

        if not tool_calls:
            feedback = (
                "WARNINGS: Your response contained no tool calls. "
                "Please use execute_commands to run commands."
            )
            return commands, is_task_complete, feedback, analysis, plan, image_read

        for tool_call in tool_calls:
            function_name = tool_call.get("function", {}).get("name", "")
            arguments_str = tool_call.get("function", {}).get("arguments", "{}")

            try:
                if isinstance(arguments_str, str):
                    arguments = json.loads(arguments_str)
                else:
                    arguments = arguments_str
            except json.JSONDecodeError:
                self.logger.warning(f"Failed to parse tool arguments: {arguments_str}")
                continue

            if not isinstance(arguments, dict):
                self.logger.warning(
                    f"Tool arguments are not an object: {arguments_str!r}"
                )
                continue

            if function_name == "execute_commands":
                # Extract analysis and plan
                analysis = arguments.get("analysis", "") or ""
                plan = arguments.get("plan", "") or ""

                # Providers sometimes double-encode the command list as a JSON
                # string, or emit a single command object instead of a list
                cmds = arguments.get("commands", [])
                if isinstance(cmds, str):
                    try:
                        cmds = json.loads(cmds)
                    except json.JSONDecodeError:
                        self.logger.warning(f"Failed to parse commands: {cmds}")
                        cmds = []
                if isinstance(cmds, dict):
                    cmds = [cmds]
                if not isinstance(cmds, list):
                    cmds = []

                for cmd in cmds:
                    try:
                        if isinstance(cmd, str):
                            cmd = json.loads(cmd)
                        if not isinstance(cmd, dict):
                            self.logger.warning(
                                f"Skipping malformed command entry: {cmd!r}"
                            )
                            continue
                        keystrokes = cmd.get("keystrokes", "")
                        if keystrokes is None:
                            keystrokes = ""
                        if not isinstance(keystrokes, str):
                            keystrokes = str(keystrokes)
                        duration = self._coerce_duration(cmd.get("duration", 1.0))
                        commands.append(
                            Command(
                                keystrokes=keystrokes,
                                duration_sec=duration,
                            )
                        )
                    except (ValueError, TypeError, json.JSONDecodeError) as exc:
                        self.logger.warning(
                            f"Skipping malformed command {cmd!r}: {exc}"
                        )
                        continue
            elif function_name == "task_complete":
                # Mark task as complete
                is_task_complete = True
            elif function_name == "image_read":
                # Extract image read request
                file_path = arguments.get("file_path", "")
                instruction = arguments.get("image_read_instruction", "")
                if file_path and instruction:
                    image_read = ImageReadRequest(
                        file_path=file_path,
                        image_read_instruction=instruction,
                    )
                else:
                    feedback = (
                        "WARNINGS: image_read requires both file_path and "
                        "image_read_instruction arguments."
                    )
            else:
                # Unknown function name - provide feedback
                feedback = (
                    f"WARNINGS: Unknown function '{function_name}'. "
                    "Please use execute_commands, task_complete, or image_read."
                )
                self.logger.warning(f"Unknown function called: {function_name}")

        return commands, is_task_complete, feedback, analysis, plan, image_read

    async def _handle_llm_interaction(
        self,
        chat: Chat,
        prompt: str,
        original_instruction: str = "",
        session: TmuxSession | None = None,
    ) -> tuple[
        list[Command], bool, str, str, str, LLMResponse, ImageReadRequest | None
    ]:
        """Native-tool interaction identical to the base harness.

        The only delta: the output-truncation retry path preserves
        reasoning_content on the stored assistant message when
        _preserve_reasoning_content is enabled, matching the normal and
        context-summarization paths so outbound tool continuations always carry
        the provider's complete reasoning field.
        """
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
            if (
                getattr(self, "_preserve_reasoning_content", False)
                and tool_response.reasoning_content
            ):
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
            if (
                getattr(self, "_preserve_reasoning_content", False)
                and tool_response.reasoning_content
            ):
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
            if (
                getattr(self, "_preserve_reasoning_content", False)
                and tool_response.reasoning_content
            ):
                assistant_message["reasoning_content"] = tool_response.reasoning_content
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