"""Tests for shared backend utilities."""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel, Field
from typing import Optional

from teamwork.backend_utils import (
    build_backend_summary,
    create_backend_from_config,
    get_api_key,
    get_model_name_from_backend,
    sanitize_model_name_for_summary,
)
from teamwork.backends import LLMBackend


class MockConfig(BaseModel):
    """Mock config for testing."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None


class MockBackendConfig(BaseModel):
    """Mock backend config for testing."""
    provider: str = Field(description="Provider name")
    model: Optional[str] = Field(default=None, description="Model name")
    temperature: Optional[float] = Field(default=None, description="Temperature")


def test_get_api_key_openai():
    """Test get_api_key retrieves OpenAI API key."""
    config = MockConfig(openai_api_key="test-openai-key")
    assert get_api_key(config, "openai") == "test-openai-key"


def test_get_api_key_anthropic():
    """Test get_api_key retrieves Anthropic API key."""
    config = MockConfig(anthropic_api_key="test-anthropic-key")
    assert get_api_key(config, "anthropic") == "test-anthropic-key"


def test_get_api_key_gemini():
    """Test get_api_key retrieves OpenRouter API key for gemini provider."""
    config = MockConfig(openrouter_api_key="test-openrouter-key")
    assert get_api_key(config, "gemini") == "test-openrouter-key"


def test_get_api_key_missing_openai():
    """Test get_api_key raises error when OpenAI key is missing."""
    config = MockConfig()
    with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
        get_api_key(config, "openai")


def test_get_api_key_missing_anthropic():
    """Test get_api_key raises error when Anthropic key is missing."""
    config = MockConfig()
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not found"):
        get_api_key(config, "anthropic")


def test_get_api_key_missing_openrouter():
    """Test get_api_key raises error when OpenRouter key is missing for gemini."""
    config = MockConfig()
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY not found"):
        get_api_key(config, "gemini")


def test_get_api_key_unknown_provider():
    """Test get_api_key raises error for unknown provider."""
    config = MockConfig()
    with pytest.raises(ValueError, match="Unknown provider"):
        get_api_key(config, "unknown")


def test_sanitize_model_name_for_summary():
    """Test sanitize_model_name_for_summary replaces special characters."""
    assert sanitize_model_name_for_summary("google/gemini-2.0-flash") == "google/gemini_2_0_flash"
    assert sanitize_model_name_for_summary("gpt-4o:2024") == "gpt_4o_2024"
    assert sanitize_model_name_for_summary("simple_model") == "simple_model"


def test_get_model_name_from_backend():
    """Test get_model_name_from_backend extracts model name from backend."""
    mock_backend = Mock(spec=LLMBackend)
    mock_backend.model = "google/gemini-2.0-flash"
    assert get_model_name_from_backend(mock_backend, "gemini") == "google/gemini-2.0-flash"


def test_get_model_name_from_backend_fallback():
    """Test get_model_name_from_backend falls back to provider if no model attribute."""
    mock_backend = Mock(spec=LLMBackend)
    del mock_backend.model
    assert get_model_name_from_backend(mock_backend, "gemini") == "gemini"


def test_build_backend_summary():
    """Test build_backend_summary creates summary string from backend configs."""
    backend_configs = [
        MockBackendConfig(provider="openai", model="gpt-4o"),
        MockBackendConfig(provider="anthropic", model="claude-3-5-haiku"),
        MockBackendConfig(provider="gemini"),
    ]
    summary = build_backend_summary(backend_configs)
    assert "openai_gpt_4o" in summary
    assert "anthropic_claude_3_5_haiku" in summary
    assert "gemini" in summary


def test_build_backend_summary_no_models():
    """Test build_backend_summary handles configs without models."""
    backend_configs = [
        MockBackendConfig(provider="openai"),
        MockBackendConfig(provider="gemini"),
    ]
    summary = build_backend_summary(backend_configs)
    assert summary == "openai-gemini"


@patch('teamwork.backend_utils.create_backend')
def test_create_backend_from_config(mock_create_backend):
    """Test create_backend_from_config creates backend with correct parameters."""
    mock_backend = Mock(spec=LLMBackend)
    mock_create_backend.return_value = mock_backend
    
    backend_cfg = MockBackendConfig(
        provider="gemini",
        model="google/gemini-2.5-pro",
        temperature=0.7
    )
    
    result = create_backend_from_config(
        backend_cfg=backend_cfg,
        api_key="test-key",
        seed=42
    )
    
    mock_create_backend.assert_called_once_with(
        provider="gemini",
        api_key="test-key",
        model="google/gemini-2.5-pro",
        seed=42,
        temperature=0.7
    )
    assert result == mock_backend


@patch('teamwork.backend_utils.create_backend')
def test_create_backend_from_config_no_temperature(mock_create_backend):
    """Test create_backend_from_config works without temperature."""
    mock_backend = Mock(spec=LLMBackend)
    mock_create_backend.return_value = mock_backend
    
    backend_cfg = MockBackendConfig(
        provider="gemini",
        model="google/gemini-2.5-flash"
    )
    
    result = create_backend_from_config(
        backend_cfg=backend_cfg,
        api_key="test-key",
        seed=42
    )
    
    mock_create_backend.assert_called_once_with(
        provider="gemini",
        api_key="test-key",
        model="google/gemini-2.5-flash",
        seed=42
    )
    assert result == mock_backend

