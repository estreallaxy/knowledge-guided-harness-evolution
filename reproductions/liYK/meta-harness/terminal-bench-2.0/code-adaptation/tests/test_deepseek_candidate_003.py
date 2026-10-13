"""Validate the observed parser defect and real interaction recovery branches.

Synthetic agent responses only: no model API, benchmark task, or verifier data.
"""
import asyncio
import json
import math
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from agents.baseline_kira import ToolCallResponse
from agents.deepseek_kira import AgentHarness as Baseline
from agents.deepseek_candidate_003 import AgentHarness as Candidate
from harbor.llms.base import ContextLengthExceededError, OutputLengthExceededError
from harbor.models.metric import UsageInfo


def tool(name, arguments):
    return {'id': 'synthetic-call', 'type': 'function',
            'function': {'name': name, 'arguments': json.dumps(arguments)}}


def agent(cls):
    instance = object.__new__(cls)
    instance.logger = Mock()
    instance._api_request_times = []
    instance._enable_summarize = True
    return instance


class ParserTests(unittest.TestCase):
    def test_observed_string_duration_crashes_h0_and_is_accepted_by_candidate(self):
        calls = [tool('execute_commands', {'commands': [
            {'keystrokes': 'printf synthetic\\n', 'duration': '5'}]})]
        with self.assertRaises(TypeError):
            agent(Baseline)._parse_tool_calls(calls)
        commands, complete, _, _, _, _ = agent(Candidate)._parse_tool_calls(calls)
        self.assertEqual(commands[0].duration_sec, 5.0)
        self.assertEqual(commands[0].keystrokes, 'printf synthetic\\n')
        self.assertFalse(complete)

    def test_valid_native_commands_completion_and_image_request_match_h0(self):
        for calls in ([tool('execute_commands', {'analysis': 'analysis', 'plan': 'plan',
                        'commands': [{'keystrokes': 'printf synthetic\\n', 'duration': 1.5}]})],
                      [tool('task_complete', {})],
                      [tool('image_read', {'file_path': '/synthetic/image.png',
                                           'image_read_instruction': 'describe'})]):
            with self.subTest(calls=calls):
                self.assertEqual(agent(Baseline)._parse_tool_calls(calls),
                                 agent(Candidate)._parse_tool_calls(calls))

    def test_invalid_duration_and_command_containers_do_not_escape_or_extend_wait(self):
        for duration in (None, '', 'invalid', 'nan', 'inf', '-inf', -5, 100, True, {}, []):
            with self.subTest(duration=duration):
                calls = [tool('execute_commands', {'commands': [
                    None, {'keystrokes': 'printf synthetic\\n', 'duration': duration}]})]
                commands = agent(Candidate)._parse_tool_calls(calls)[0]
                self.assertEqual(len(commands), 1)
                self.assertTrue(math.isfinite(commands[0].duration_sec))
                self.assertTrue(0 <= commands[0].duration_sec <= 60)
        encoded = json.dumps([{'keystrokes': 'printf synthetic\\n', 'duration': '2.5'}])
        self.assertEqual(agent(Candidate)._parse_tool_calls([
            tool('execute_commands', {'commands': encoded})])[0][0].duration_sec, 2.5)

    def test_model_provider_thinking_call_and_native_run_remain_inherited(self):
        for method in ('run', '_call_llm_with_tools', '_provider_completion_kwargs'):
            self.assertIs(getattr(Candidate, method), getattr(Baseline, method))
        self.assertEqual(Candidate._policy_path, Baseline._policy_path)


class InteractionTests(unittest.IsolatedAsyncioTestCase):
    async def interaction(self, cls, mode='normal', summary_failure=False, continuation=False):
        instance = agent(cls)
        usage = UsageInfo(prompt_tokens=11, completion_tokens=7, cache_tokens=2, cost_usd=0.01)
        response = ToolCallResponse(content='synthetic', tool_calls=[tool('execute_commands',
            {'commands': [{'keystrokes': 'printf synthetic\\n', 'duration': 1}]})],
            reasoning_content='full-synthetic-reasoning', usage=usage)
        responses = [response]
        if mode != 'normal':
            error = OutputLengthExceededError if mode == 'output' else ContextLengthExceededError
            responses.insert(0, error('synthetic'))
        if continuation:
            responses.append(response)
        instance._call_llm_with_tools = AsyncMock(side_effect=responses)
        instance._unwind_messages_to_free_tokens = Mock()
        instance._summarize = AsyncMock(side_effect=RuntimeError('synthetic')) if summary_failure else AsyncMock(return_value=('summary', []))
        async def passthrough(coro):
            return await coro
        instance._with_block_timeout = passthrough
        messages = [{'role': 'assistant', 'content': 'previous',
                     'reasoning_content': 'complete-existing-reasoning'}]
        chat = SimpleNamespace(messages=messages, _messages=messages, reset_response_chain=Mock(),
                               _cumulative_input_tokens=0, _cumulative_output_tokens=0,
                               _cumulative_cache_tokens=0, _cumulative_cost=0)
        session = SimpleNamespace(capture_pane=AsyncMock(return_value='synthetic-screen'))
        await instance._handle_llm_interaction(chat, 'prompt', 'synthetic-instruction', session=session)
        if continuation:
            await instance._handle_llm_interaction(chat, 'next prompt', session=session)
        return instance, chat

    async def test_normal_and_context_recovery_match_h0_and_preserve_usage(self):
        for mode in ('normal', 'context'):
            with self.subTest(mode=mode):
                _, baseline = await self.interaction(Baseline, mode)
                instance, candidate = await self.interaction(Candidate, mode)
                self.assertEqual(candidate.messages, baseline.messages)
                self.assertEqual(candidate._cumulative_input_tokens, 11)
                self.assertEqual(candidate._cumulative_output_tokens, 7)
                self.assertEqual(candidate._cumulative_cache_tokens, 2)
                self.assertAlmostEqual(candidate._cumulative_cost, 0.01)
                self.assertEqual(len(instance._api_request_times), 1)

    async def test_output_recovery_preserves_complete_reasoning_in_next_outbound_call(self):
        _, baseline = await self.interaction(Baseline, 'output')
        self.assertNotIn('reasoning_content', baseline.messages[-2])
        instance, candidate = await self.interaction(Candidate, 'output', continuation=True)
        outbound = instance._call_llm_with_tools.await_args_list[-1].args[0]
        assistant = next(message for message in outbound if message.get('tool_calls'))
        self.assertEqual(assistant['reasoning_content'], 'full-synthetic-reasoning')
        self.assertEqual(outbound[0]['reasoning_content'], 'complete-existing-reasoning')
        self.assertTrue(any(message.get('tool_call_id') == assistant['tool_calls'][0]['id']
                            for message in outbound))
        self.assertEqual(candidate._cumulative_input_tokens, 22)
        self.assertEqual(candidate._cumulative_output_tokens, 14)

    async def test_failed_summarization_fallback_matches_h0(self):
        _, baseline = await self.interaction(Baseline, 'context', summary_failure=True)
        _, candidate = await self.interaction(Candidate, 'context', summary_failure=True)
        self.assertEqual(candidate.messages, baseline.messages)

    async def test_native_cancellation_is_propagated_without_retry_or_fake_usage(self):
        instance = agent(Candidate)
        instance._call_llm_with_tools = AsyncMock(side_effect=asyncio.CancelledError)
        messages = []
        chat = SimpleNamespace(messages=messages, _messages=messages)
        with self.assertRaises(asyncio.CancelledError):
            await instance._handle_llm_interaction(chat, 'prompt')
        self.assertEqual(instance._call_llm_with_tools.await_count, 1)
        self.assertEqual(instance._api_request_times, [])
        self.assertEqual(messages, [])


if __name__ == '__main__':
    unittest.main()
