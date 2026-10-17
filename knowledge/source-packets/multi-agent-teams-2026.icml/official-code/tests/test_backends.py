"""Tests for LLM backend implementations."""

import pytest
from unittest.mock import Mock, patch
from teamwork.backends import AnthropicBackend, EchoBackend, LLMBackend, OpenAIBackend, OpenRouterBackend, create_backend
from teamwork.conversation import Trajectory, Turn
from teamwork.profiles import AgentProfile


class MockLLMBackend(LLMBackend):
    """Mock backend for testing the abstract interface."""

    def __init__(self, response: str = "mock response", seed=None):
        super().__init__(seed)
        self.response = response
        self.last_agent_profile = None
        self.last_trajectory = None
        self.call_count = 0

    def invoke(self, *, agent_profile, trajectory) -> str:
        self.last_agent_profile = agent_profile
        self.last_trajectory = trajectory
        self.call_count += 1
        return self.response


class AsyncMockBackend(LLMBackend):
    """Mock backend that overrides ainvoke for async testing."""

    def __init__(self, sync_response: str = "sync", async_response: str = "async", seed=None):
        super().__init__(seed)
        self.sync_response = sync_response
        self.async_response = async_response
        self.sync_calls = 0
        self.async_calls = 0

    def invoke(self, *, agent_profile, trajectory) -> str:
        self.sync_calls += 1
        return self.sync_response

    async def ainvoke(self, *, agent_profile, trajectory) -> str:
        self.async_calls += 1
        return self.async_response


def test_echo_backend_basic():
    """Test EchoBackend basic functionality."""
    backend = EchoBackend()
    agent_profile = AgentProfile(
        agent_id=1,
        name="Test",
        role="tester",
        system_prompt="Hello world"
    )
    trajectory = Trajectory()

    result = backend.invoke(agent_profile=agent_profile, trajectory=trajectory)
    assert "[echo]" in result and "Hello world" in result


def test_echo_backend_with_conversation():
    """Test EchoBackend with conversation history."""
    backend = EchoBackend()
    agent_profile = AgentProfile(
        agent_id=1,
        name="TestAgent",
        role="tester",
        system_prompt="Test system"
    )
    trajectory = Trajectory()
    trajectory.append(Turn(speaker_id=2, content="Hello"))

    result = backend.invoke(agent_profile=agent_profile, trajectory=trajectory)
    assert "[echo]" in result
    assert "Test system" in result
    assert "Agent 2: Hello" in result


def test_mock_backend_tracks_calls():
    """Test that MockLLMBackend properly tracks invocation details."""
    backend = MockLLMBackend("custom response")
    agent_profile = AgentProfile(agent_id=5, name="TestAgent", role="tester", system_prompt="Test")
    trajectory = Trajectory()
    trajectory.append(Turn(speaker_id=1, content="hello"))

    result = backend.invoke(agent_profile=agent_profile, trajectory=trajectory)

    assert result == "custom response"
    assert backend.last_agent_profile == agent_profile
    assert backend.last_trajectory == trajectory
    assert backend.call_count == 1


def test_mock_backend_multiple_calls():
    """Test MockLLMBackend with multiple invocations."""
    backend = MockLLMBackend("response")
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    # Make multiple calls
    backend.invoke(agent_profile=agent_profile, trajectory=trajectory)
    backend.invoke(agent_profile=agent_profile, trajectory=trajectory)
    backend.invoke(agent_profile=agent_profile, trajectory=trajectory)

    # Should track call count
    assert backend.call_count == 3



def test_llm_backend_default_ainvoke():
    """Test that default ainvoke calls invoke method."""
    backend = MockLLMBackend("test response")
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    # Test the default async implementation
    import asyncio
    async def test_async():
        result = await backend.ainvoke(agent_profile=agent_profile, trajectory=trajectory)
        return result

    result = asyncio.run(test_async())

    assert result == "test response"
    assert backend.call_count == 1


def test_backend_with_custom_ainvoke():
    """Test backend that overrides ainvoke method."""
    backend = AsyncMockBackend("sync response", "async response")
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    # Test sync call
    sync_result = backend.invoke(agent_profile=agent_profile, trajectory=trajectory)
    assert sync_result == "sync response"
    assert backend.sync_calls == 1
    assert backend.async_calls == 0

    # Test async call
    import asyncio
    async def test_async():
        return await backend.ainvoke(agent_profile=agent_profile, trajectory=trajectory)

    async_result = asyncio.run(test_async())
    assert async_result == "async response"
    assert backend.sync_calls == 1  # Should not increment
    assert backend.async_calls == 1


def test_backend_with_complex_data():
    """Test backends with complex agent profiles and trajectories."""
    backend = MockLLMBackend("complex response")

    complex_agent_profile = AgentProfile(
        agent_id=42,
        name="ComplexAgent",
        role="tester",
        system_prompt="Complex system prompt",
        metadata={
            "version": "1.2.3",
            "capabilities": ["reasoning", "memory"],
            "config": {"temperature": 0.7, "max_tokens": 100}
        }
    )

    complex_trajectory = Trajectory()
    complex_trajectory.append(Turn(speaker_id=1, content="First message"))
    complex_trajectory.append(Turn(speaker_id=2, content="Second message"))
    complex_trajectory.append(Turn(speaker_id=1, content="Third message"))

    result = backend.invoke(
        agent_profile=complex_agent_profile,
        trajectory=complex_trajectory
    )

    assert result == "complex response"
    assert backend.last_agent_profile == complex_agent_profile
    assert backend.last_trajectory == complex_trajectory


@patch('openai.OpenAI')
def test_openai_backend_init(mock_openai_class):
    """Test OpenAI backend initialization."""
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    backend = OpenAIBackend(api_key="test-key", model="gpt-3.5-turbo", temperature=0.7)

    mock_openai_class.assert_called_once_with(api_key="test-key")
    assert backend.client == mock_client
    assert backend.model == "gpt-3.5-turbo"
    assert backend.extra_params == {"temperature": 0.7}



@patch('openai.OpenAI')
def test_openai_backend_basic_invoke(mock_openai_class):
    """Test OpenAI backend basic functionality with new interface."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "OpenAI response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20

    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    backend = OpenAIBackend(api_key="test-key", temperature=0.5)
    agent_profile = AgentProfile(
        agent_id=2,
        name="TestAgent",
        role="assistant",
        system_prompt="You are a helpful assistant"
    )
    trajectory = Trajectory.from_dict({
        "turns": [
            {"speaker_id": 1, "content": "Hello"},
            {"speaker_id": 2, "content": "Hi there"}
        ]
    })

    result = backend.invoke(
        agent_profile=agent_profile,
        trajectory=trajectory
    )

    assert result == "OpenAI response"
    mock_client.chat.completions.create.assert_called_once()

    # Verify the call structure
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]['messages']

    # Should have system message, conversation history, and instruction
    assert len(messages) >= 4
    assert messages[0]['role'] == 'system'
    assert "helpful assistant" in messages[0]['content']


@patch('openai.OpenAI')
def test_openai_backend_api_error(mock_openai_class):
    """Test OpenAI backend handles API errors gracefully."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai_class.return_value = mock_client

    backend = OpenAIBackend(api_key="test-key")
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    with pytest.raises(RuntimeError, match="OpenAI API call failed: API Error"):
        backend.invoke(agent_profile=agent_profile, trajectory=trajectory)


def test_echo_backend_with_seed():
    """Test EchoBackend includes seed in output."""
    backend = EchoBackend(seed=42)
    agent_profile = AgentProfile(agent_id=1, name="Test", role="tester", system_prompt="Test")
    trajectory = Trajectory()

    result = backend.invoke(agent_profile=agent_profile, trajectory=trajectory)
    assert "[echo [seed=42]]" in result


def test_echo_backend_without_seed():
    """Test EchoBackend without seed doesn't include seed in output."""
    backend = EchoBackend()
    agent_profile = AgentProfile(agent_id=1, name="Test", role="tester", system_prompt="Test")
    trajectory = Trajectory()

    result = backend.invoke(agent_profile=agent_profile, trajectory=trajectory)
    assert "[echo]" in result
    assert "seed" not in result


@patch('openai.OpenAI')
def test_openai_backend_with_seed(mock_openai_class):
    """Test OpenAI backend passes seed to API when provided."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    backend = OpenAIBackend(api_key="test-key", seed=42)
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    backend.invoke(agent_profile=agent_profile, trajectory=trajectory)

    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["seed"] == 42


@patch('openai.OpenAI')
def test_openai_backend_without_seed(mock_openai_class):
    """Test OpenAI backend doesn't pass seed when not provided."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    backend = OpenAIBackend(api_key="test-key")
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    backend.invoke(agent_profile=agent_profile, trajectory=trajectory)

    call_args = mock_client.chat.completions.create.call_args
    assert "seed" not in call_args[1]


@patch('anthropic.Anthropic')
def test_anthropic_backend_init(mock_anthropic_class):
    """Test Anthropic backend initialization."""
    mock_client = Mock()
    mock_anthropic_class.return_value = mock_client

    backend = AnthropicBackend(api_key="test-key", model="claude-3-5-sonnet-20241022", temperature=0.7)

    mock_anthropic_class.assert_called_once_with(api_key="test-key")
    assert backend.client == mock_client
    assert backend.model == "claude-3-5-sonnet-20241022"
    assert backend.extra_params == {"temperature": 0.7}


@patch('anthropic.Anthropic')
def test_anthropic_backend_basic_invoke(mock_anthropic_class):
    """Test Anthropic backend basic functionality."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = "Anthropic response"
    mock_response.usage = Mock()
    mock_response.usage.input_tokens = 15
    mock_response.usage.output_tokens = 25

    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    backend = AnthropicBackend(api_key="test-key", temperature=0.5)
    agent_profile = AgentProfile(
        agent_id=2,
        name="TestAgent",
        role="assistant",
        system_prompt="You are a helpful assistant"
    )
    trajectory = Trajectory.from_dict({
        "turns": [
            {"speaker_id": 1, "content": "Hello"},
            {"speaker_id": 2, "content": "Hi there"}
        ]
    })

    result = backend.invoke(
        agent_profile=agent_profile,
        trajectory=trajectory
    )

    assert result == "Anthropic response"
    mock_client.messages.create.assert_called_once()

    # Verify the call structure
    call_args = mock_client.messages.create.call_args
    assert "system" in call_args[1]
    assert "helpful assistant" in call_args[1]["system"]
    assert "messages" in call_args[1]


@patch('anthropic.Anthropic')
def test_anthropic_backend_api_error(mock_anthropic_class):
    """Test Anthropic backend handles API errors gracefully."""
    mock_client = Mock()
    mock_client.messages.create.side_effect = Exception("API Error")
    mock_anthropic_class.return_value = mock_client

    backend = AnthropicBackend(api_key="test-key")
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    with pytest.raises(RuntimeError, match="Anthropic API call failed: API Error"):
        backend.invoke(agent_profile=agent_profile, trajectory=trajectory)


@patch('openai.OpenAI')
def test_openrouter_backend_init(mock_openai_class):
    """Test OpenRouter backend initialization."""
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    backend = OpenRouterBackend(api_key="test-key", model="google/gemini-2.0-flash", temperature=0.7)

    mock_openai_class.assert_called_once_with(
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1"
    )
    assert backend.client == mock_client
    assert backend.model == "google/gemini-2.0-flash"
    assert backend.extra_params == {"temperature": 0.7}


@patch('openai.OpenAI')
def test_openrouter_backend_basic_invoke(mock_openai_class):
    """Test OpenRouter backend basic functionality."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "OpenRouter response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20

    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    backend = OpenRouterBackend(api_key="test-key", model="google/gemini-2.0-flash", temperature=0.5)
    agent_profile = AgentProfile(
        agent_id=2,
        name="TestAgent",
        role="assistant",
        system_prompt="You are a helpful assistant"
    )
    trajectory = Trajectory.from_dict({
        "turns": [
            {"speaker_id": 1, "content": "Hello"},
            {"speaker_id": 2, "content": "Hi there"}
        ]
    })

    result = backend.invoke(
        agent_profile=agent_profile,
        trajectory=trajectory
    )

    assert result == "OpenRouter response"
    mock_client.chat.completions.create.assert_called_once()

    # Verify the call structure
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]['messages']

    # Should have system message, conversation history, and instruction
    assert len(messages) >= 4
    assert messages[0]['role'] == 'system'
    assert "helpful assistant" in messages[0]['content']


@patch('openai.OpenAI')
def test_openrouter_backend_api_error(mock_openai_class):
    """Test OpenRouter backend handles API errors gracefully."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai_class.return_value = mock_client

    backend = OpenRouterBackend(api_key="test-key", model="google/gemini-2.0-flash")
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    with pytest.raises(RuntimeError, match="OpenRouter API call failed: API Error"):
        backend.invoke(agent_profile=agent_profile, trajectory=trajectory)


@patch('openai.OpenAI')
def test_openrouter_backend_with_seed(mock_openai_class):
    """Test OpenRouter backend passes seed to API when provided."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    backend = OpenRouterBackend(api_key="test-key", model="google/gemini-2.0-flash", seed=42)
    agent_profile = AgentProfile(agent_id=1, name="Test", role="test", system_prompt="Test")
    trajectory = Trajectory()

    backend.invoke(agent_profile=agent_profile, trajectory=trajectory)

    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["seed"] == 42


@patch('openai.OpenAI')
def test_create_backend_gemini_default(mock_openai_class):
    """Test create_backend with gemini provider uses default model."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    backend = create_backend(provider="gemini", api_key="test-key")
    assert isinstance(backend, OpenRouterBackend)
    assert backend.model == "google/gemini-2.0-flash"


@patch('openai.OpenAI')
def test_create_backend_gemini_override(mock_openai_class):
    """Test create_backend with gemini provider can override model."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"
    mock_response.usage = Mock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    backend = create_backend(provider="gemini", api_key="test-key", model="google/gemini-2.5-pro")
    assert isinstance(backend, OpenRouterBackend)
    assert backend.model == "google/gemini-2.5-pro"


def test_create_backend_unsupported_provider():
    """Test create_backend raises error for unsupported provider."""
    with pytest.raises(ValueError, match="Unsupported provider: invalid"):
        create_backend(provider="invalid", api_key="test-key")


