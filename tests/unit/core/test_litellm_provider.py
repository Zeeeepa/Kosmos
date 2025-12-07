"""
Unit tests for LiteLLMProvider.

Tests using REAL LiteLLM API calls (not mocks).
Requires ANTHROPIC_API_KEY or DEEPSEEK_API_KEY environment variable.
Uses cheaper models for cost-effective testing.
"""

import os
import pytest
import uuid

# Skip all tests if litellm is not installed
pytest.importorskip("litellm")

from kosmos.core.providers.litellm_provider import LiteLLMProvider
from kosmos.core.providers.base import LLMResponse, Message


# Skip if no API keys
pytestmark = [
    pytest.mark.requires_claude,
    pytest.mark.skipif(
        not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("DEEPSEEK_API_KEY")),
        reason="Requires ANTHROPIC_API_KEY or DEEPSEEK_API_KEY for real LLM calls"
    )
]


def unique_prompt(base: str) -> str:
    """Add unique suffix to avoid cache hits."""
    return f"{base} [test-id: {uuid.uuid4().hex[:8]}]"


class TestLiteLLMProviderInit:
    """Test LiteLLMProvider initialization."""

    def test_init_with_model_only(self):
        """Test initialization with just a model name."""
        provider = LiteLLMProvider({"model": "gpt-3.5-turbo"})

        assert provider.model == "gpt-3.5-turbo"
        assert provider.max_tokens_default == 4096
        assert provider.temperature_default == 0.7

    def test_init_with_anthropic_model(self):
        """Test initialization with Anthropic model."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")

        provider = LiteLLMProvider({
            "model": "claude-3-haiku-20240307",
            "api_key": api_key
        })

        assert provider.model == "claude-3-haiku-20240307"
        assert provider.provider_type == "anthropic"

    def test_init_with_deepseek_model(self):
        """Test initialization with DeepSeek model."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("DEEPSEEK_API_KEY not set")

        provider = LiteLLMProvider({
            "model": "deepseek/deepseek-chat",
            "api_key": api_key
        })

        assert provider.model == "deepseek/deepseek-chat"
        assert provider.provider_type == "deepseek"

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        provider = LiteLLMProvider({
            "model": "gpt-4-turbo",
            "max_tokens": 8192,
            "temperature": 0.5,
            "timeout": 60
        })

        assert provider.max_tokens_default == 8192
        assert provider.temperature_default == 0.5
        assert provider.timeout == 60


class TestLiteLLMProviderGenerateWithAnthropic:
    """Test LiteLLMProvider generation with Anthropic."""

    @pytest.fixture
    def anthropic_provider(self):
        """Create a provider with Anthropic."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")

        return LiteLLMProvider({
            "model": "claude-3-haiku-20240307",
            "api_key": api_key,
            "max_tokens": 100,
            "temperature": 0.0
        })

    def test_generate_basic(self, anthropic_provider):
        """Test basic text generation with Anthropic via LiteLLM."""
        response = anthropic_provider.generate(
            prompt=unique_prompt("Say 'hello' and nothing else.")
        )

        assert isinstance(response, LLMResponse)
        assert response.content is not None
        assert len(response.content) > 0
        # Usage stats are in the usage object
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0

    def test_generate_with_system_prompt(self, anthropic_provider):
        """Test generation with system prompt."""
        response = anthropic_provider.generate(
            prompt=unique_prompt("What do you help with?"),
            system="You are a math tutor. Always mention math."
        )

        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0

    def test_generate_structured(self, anthropic_provider):
        """Test structured JSON generation."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            }
        }

        result = anthropic_provider.generate_structured(
            prompt=unique_prompt("Generate JSON with name='test' and value=42"),
            schema=schema
        )

        assert isinstance(result, dict)

    def test_usage_tracking(self, anthropic_provider):
        """Test usage statistics are tracked."""
        # Make a request
        response = anthropic_provider.generate(prompt=unique_prompt("Hi"))

        # Usage is tracked in the response
        assert response.usage is not None
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0


class TestLiteLLMProviderGenerateWithDeepSeek:
    """Test LiteLLMProvider generation with DeepSeek."""

    @pytest.fixture
    def deepseek_provider(self):
        """Create a provider with DeepSeek."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("DEEPSEEK_API_KEY not set")

        return LiteLLMProvider({
            "model": "deepseek/deepseek-chat",
            "api_key": api_key,
            "max_tokens": 100,
            "temperature": 0.0
        })

    def test_generate_basic(self, deepseek_provider):
        """Test basic text generation with DeepSeek via LiteLLM."""
        response = deepseek_provider.generate(
            prompt=unique_prompt("Say 'hello' and nothing else.")
        )

        assert isinstance(response, LLMResponse)
        assert response.content is not None
        assert len(response.content) > 0

    def test_generate_with_system_prompt(self, deepseek_provider):
        """Test generation with system prompt."""
        response = deepseek_provider.generate(
            prompt=unique_prompt("What do you help with?"),
            system="You are a math tutor. Always mention math."
        )

        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0


class TestLiteLLMProviderMessages:
    """Test message-based generation."""

    @pytest.fixture
    def provider(self):
        """Create a provider with available API key."""
        if os.getenv("ANTHROPIC_API_KEY"):
            return LiteLLMProvider({
                "model": "claude-3-haiku-20240307",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "max_tokens": 100,
                "temperature": 0.0
            })
        elif os.getenv("DEEPSEEK_API_KEY"):
            return LiteLLMProvider({
                "model": "deepseek/deepseek-chat",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "max_tokens": 100,
                "temperature": 0.0
            })
        else:
            pytest.skip("No API key available")

    def test_generate_with_messages(self, provider):
        """Test multi-turn conversation."""
        messages = [
            Message(role="user", content="My name is Alice."),
            Message(role="assistant", content="Hello Alice!"),
            Message(role="user", content=unique_prompt("What is my name?"))
        ]

        response = provider.generate_with_messages(messages)

        assert isinstance(response, LLMResponse)
        assert "alice" in response.content.lower()


class TestLiteLLMProviderErrorHandling:
    """Test error handling."""

    def test_invalid_model(self):
        """Test handling of invalid model."""
        provider = LiteLLMProvider({
            "model": "invalid-model-xyz",
            "api_key": "invalid-key"
        })

        with pytest.raises(Exception):
            provider.generate(prompt="Test")

    def test_missing_api_key(self):
        """Test handling when API key is missing for providers that need it."""
        # Create provider without API key for a model that needs one
        provider = LiteLLMProvider({
            "model": "claude-3-haiku-20240307"
            # No api_key provided
        })

        # Should fail when trying to generate (unless env var is set)
        if not os.getenv("ANTHROPIC_API_KEY"):
            with pytest.raises(Exception):
                provider.generate(prompt="Test")
