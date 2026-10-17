"""Backend interfaces for invoking language models."""

import abc
from typing import Optional
from dataclasses import dataclass

import anthropic
import openai

from .conversation import Trajectory, format_turn_content
from .profiles import AgentProfile


@dataclass
class UsageStats:
    """Track token usage across API calls."""

    input_tokens: int = 0
    output_tokens: int = 0

    def add_call(self, input_tokens: int, output_tokens: int) -> None:
        """Add token counts from a single API call."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens
        }


class LLMBackend(abc.ABC):
    """Abstract interface for LLM providers."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize backend with optional seed for reproducibility.

        Args:
            seed: Random seed for deterministic outputs (if supported by provider)
        """
        self.seed = seed
        self.usage_stats = UsageStats()

    @abc.abstractmethod
    def invoke(
        self,
        *,
        agent_profile: AgentProfile,
        trajectory: Trajectory,
    ) -> str:
        """Perform a synchronous inference call and return the model response.

        Args:
            agent_profile: Agent metadata and configuration
            trajectory: The conversation history

        Returns:
            The model's response text
        """

    async def ainvoke(
        self,
        *,
        agent_profile: AgentProfile,
        trajectory: Trajectory,
    ) -> str:
        """Async wrapper calling the synchronous method by default."""

        return self.invoke(
            agent_profile=agent_profile, trajectory=trajectory
        )

    def _build_system_message(self, agent_profile: AgentProfile) -> str:
        """Build the system message from agent profile.
        
        This method unifies the logic for building system messages across all backends,
        ensuring consistency in how agent profile information is formatted.
        
        Args:
            agent_profile: Agent metadata and configuration
            
        Returns:
            A formatted system message string
        """
        system_parts = []
        if agent_profile.system_prompt:
            system_parts.append(agent_profile.system_prompt.strip())
        if agent_profile.persona:
            system_parts.append(f"Persona: {agent_profile.persona.strip()}")
        if agent_profile.role:
            system_parts.append(f"Role: {agent_profile.role.strip()}")
        if agent_profile.hidden_context:
            system_parts.append(f"Hidden context: {agent_profile.hidden_context.strip()}")
        
        return "\n".join(system_parts)

    def format_full_prompt(
        self,
        *,
        agent_profile: AgentProfile,
        trajectory: Trajectory,
    ) -> str:
        """Format the full prompt as the agent sees it, for logging/debugging.
        
        This method returns a human-readable representation of the complete prompt
        that would be sent to the model, including system prompt and all trajectory turns.
        
        Args:
            agent_profile: Agent metadata and configuration
            trajectory: The conversation history
            
        Returns:
            A formatted string representation of the full prompt
        """
        system_message = self._build_system_message(agent_profile)
        
        # Format conversation history
        conversation_lines = []
        for turn in trajectory.turns:
            formatted_content = format_turn_content(turn, agent_profile.agent_id)
            conversation_lines.append(formatted_content)
        
        # Assemble full prompt
        prompt_sections = [system_message] if system_message else []
        if conversation_lines:
            prompt_sections.append("Conversation so far:\n" + "\n".join(conversation_lines))
        prompt_sections.append("Your turn: Respond concisely yet helpfully.")
        
        return "\n\n".join(section for section in prompt_sections if section)


class EchoBackend(LLMBackend):
    """Simple backend that mirrors the prompt for local testing."""

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed)

    def invoke(
        self,
        *,
        agent_profile: AgentProfile,
        trajectory: Trajectory,
    ) -> str:
        prompt = self.format_full_prompt(
            agent_profile=agent_profile,
            trajectory=trajectory
        )
        seed_str = f" [seed={self.seed}]" if self.seed is not None else ""
        return f"[echo{seed_str}] {prompt}".strip()


class OpenAIBackend(LLMBackend):
    """Backend for OpenAI Chat Completions API."""

    def __init__(self, api_key: str, model: str = "gpt-4o", seed: Optional[int] = None, **kwargs):
        """Initialize OpenAI backend with API key and model configuration.

        Args:
            api_key: OpenAI API key
            model: Model name (e.g., "gpt-4o", "gpt-4o-mini")
            seed: Random seed for deterministic outputs
            **kwargs: Additional parameters to pass to the API
        """
        super().__init__(seed)
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.extra_params = kwargs

    def invoke(
        self,
        *,
        agent_profile: AgentProfile,
        trajectory: Trajectory,
    ) -> str:
        """Invoke OpenAI by building messages directly from structured data."""
        current_agent_id = agent_profile.agent_id

        # Build system message from agent profile using unified method
        system_message = self._build_system_message(agent_profile)
        messages = [{"role": "system", "content": system_message}]

        # Add conversation history
        for turn in trajectory.turns:
            if turn.speaker_id == current_agent_id:
                # Current agent's previous responses
                messages.append({"role": "assistant", "content": turn.content})
            else:
                # Other agents' messages (including system messages)
                formatted_content = format_turn_content(turn, current_agent_id)
                messages.append({"role": "user", "content": formatted_content})

        # Add instruction to respond
        messages.append({"role": "user", "content": "Respond concisely yet helpfully."})

        try:
            params = {"model": self.model, "messages": messages, **self.extra_params}
            if self.seed is not None:
                params["seed"] = self.seed

            response = self.client.chat.completions.create(**params)  # type: ignore[arg-type]

            # Track token usage
            if response.usage:
                self.usage_stats.add_call(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens
                )

            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")


class AnthropicBackend(LLMBackend):
    """Backend for Anthropic Claude API."""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022", seed: Optional[int] = None, **kwargs):
        """Initialize Anthropic backend with API key and model configuration.

        Args:
            api_key: Anthropic API key
            model: Model name (e.g., "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022")
            seed: Random seed for deterministic outputs (not supported by Anthropic)
            **kwargs: Additional parameters to pass to the API
        """
        super().__init__(seed)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.extra_params = kwargs

    def invoke(
        self,
        *,
        agent_profile: AgentProfile,
        trajectory: Trajectory,
    ) -> str:
        """Invoke Anthropic API by building messages from structured data."""
        current_agent_id = agent_profile.agent_id

        # Build system message from agent profile using unified method
        system_message = self._build_system_message(agent_profile)

        # Build conversation messages (Anthropic uses user/assistant alternation)
        messages = []
        for turn in trajectory.turns:
            if turn.speaker_id == current_agent_id:
                # Current agent's previous responses
                messages.append({"role": "assistant", "content": turn.content})
            else:
                # Other agents' messages (including system messages)
                formatted_content = format_turn_content(turn, current_agent_id)
                messages.append({"role": "user", "content": formatted_content})

        # Add instruction to respond
        messages.append({"role": "user", "content": "Respond concisely yet helpfully."})

        try:
            params = {
                "model": self.model,
                "system": system_message,
                "messages": messages,
                "max_tokens": 4096,
                **self.extra_params
            }

            response = self.client.messages.create(**params)

            # Track token usage
            if response.usage:
                self.usage_stats.add_call(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens
                )

            return response.content[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"Anthropic API call failed: {e}")


class OpenRouterBackend(LLMBackend):
    """Backend for Open Router API (supports Gemini and other models)."""

    def __init__(self, api_key: str, model: str, seed: Optional[int] = None, **kwargs):
        """Initialize OpenRouter backend with API key and model configuration.

        Args:
            api_key: OpenRouter API key
            model: Model name in provider/model format (e.g., "google/gemini-2.0-flash", "google/gemini-3-pro-preview")
            seed: Random seed for deterministic outputs (if supported by the model)
            **kwargs: Additional parameters to pass to the API
        """
        super().__init__(seed)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model
        self.extra_params = kwargs

    def invoke(
        self,
        *,
        agent_profile: AgentProfile,
        trajectory: Trajectory,
    ) -> str:
        """Invoke OpenRouter API by building messages directly from structured data."""
        current_agent_id = agent_profile.agent_id

        # Build system message from agent profile using unified method
        system_message = self._build_system_message(agent_profile)
        messages = [{"role": "system", "content": system_message}]

        # Add conversation history
        for turn in trajectory.turns:
            if turn.speaker_id == current_agent_id:
                # Current agent's previous responses
                messages.append({"role": "assistant", "content": turn.content})
            else:
                # Other agents' messages (including system messages)
                formatted_content = format_turn_content(turn, current_agent_id)
                messages.append({"role": "user", "content": formatted_content})

        # Add instruction to respond
        messages.append({"role": "user", "content": "Respond concisely yet helpfully."})

        try:
            params = {"model": self.model, "messages": messages, **self.extra_params}
            if self.seed is not None:
                params["seed"] = self.seed

            response = self.client.chat.completions.create(**params)  # type: ignore[arg-type]

            # Track token usage
            if response.usage:
                self.usage_stats.add_call(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens
                )

            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenRouter API call failed: {e}")


def create_backend(
    provider: str,
    api_key: str,
    model: Optional[str] = None,
    seed: Optional[int] = None,
    **kwargs
) -> LLMBackend:
    """Create a backend instance for the specified provider.

    Args:
        provider: Backend provider name ("openai", "anthropic", or "gemini")
        api_key: API key for the provider
        model: Model name (uses provider default if None)
        seed: Random seed for deterministic outputs
        **kwargs: Additional provider-specific parameters (temperature, top_p, etc.)

    Returns:
        Configured LLMBackend instance

    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.lower()

    if provider == "openai":
        if model is None:
            return OpenAIBackend(api_key=api_key, seed=seed, **kwargs)
        return OpenAIBackend(api_key=api_key, model=model, seed=seed, **kwargs)

    elif provider == "anthropic":
        if model is None:
            return AnthropicBackend(api_key=api_key, seed=seed, **kwargs)
        return AnthropicBackend(api_key=api_key, model=model, seed=seed, **kwargs)

    elif provider == "gemini":
        default_model = "google/gemini-2.0-flash"
        model_to_use = model if model is not None else default_model
        return OpenRouterBackend(api_key=api_key, model=model_to_use, seed=seed, **kwargs)

    else:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers are: openai, anthropic, gemini"
        )
