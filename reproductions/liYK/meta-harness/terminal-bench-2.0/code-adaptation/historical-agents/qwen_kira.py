"""KIRA provider adaptation for Qwen; no task-specific prompt changes."""
import json
import os
from pathlib import Path

from agents.baseline_kira import AgentHarness as KiraHarness


POLICY = Path(__file__).resolve().parents[4] / 'configs/qwen-api.json'


class AgentHarness(KiraHarness):
    _preserve_reasoning_content = True
    _policy_path = POLICY

    def __init__(self, *args, **kwargs):
        self._qwen_policy = json.loads(self._policy_path.read_text())
        expected = 'openai/' + self._qwen_policy['model']
        if kwargs.get('model_name', expected) != expected:
            raise ValueError('Model must match the fixed Qwen policy')
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
            'timeout': self._qwen_policy['socket_timeout_seconds'],
            'extra_body': {'enable_thinking': self._qwen_policy['enable_thinking']},
        }
        kwargs['reasoning_effort'] = None
        super().__init__(*args, **kwargs)

    async def _with_block_timeout(self, coro, timeout_sec=None):
        # Includes summary calls: the outer 600s guard must not cut thinking short.
        return await super()._with_block_timeout(
            coro, timeout_sec if timeout_sec is not None else self._qwen_policy['socket_timeout_seconds']
        )

    def _provider_completion_kwargs(self, kwargs: dict) -> dict:
        result = dict(kwargs)
        result.pop('reasoning_effort', None)
        result.pop('max_tokens', None)
        result.update({
            'api_key': os.environ['BAILIAN_API_KEY'],
            'api_base': os.environ['BAILIAN_OPENAI_COMPATIBLE'],
            'timeout': self._qwen_policy['socket_timeout_seconds'],
            'drop_params': False,
            'extra_body': {
                'enable_thinking': self._qwen_policy['enable_thinking'],
            },
        })
        if result.get('temperature') is None:
            result.pop('temperature', None)
        return result
