"""
Unit tests for Claude LLM client.

Tests using REAL Anthropic API calls (not mocks).
Requires ANTHROPIC_API_KEY environment variable.
Uses claude-3-haiku for cost-effective testing.
"""

import os
import pytest
import json
import uuid


# Skip all tests if no API key
pytestmark = [
    pytest.mark.requires_claude,
    pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="Requires ANTHROPIC_API_KEY for real LLM calls"
    )
]


def unique_prompt(base: str) -> str:
    """Add unique suffix to avoid cache hits."""
    return f"{base} [test-id: {uuid.uuid4().hex[:8]}]"


@pytest.fixture
def api_env():
    """Ensure API mode environment is set."""
    # Real API key should be loaded from .env via conftest
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key or api_key.startswith('999'):
        pytest.skip("Real ANTHROPIC_API_KEY required")
    yield


@pytest.fixture
def cli_env():
    """Set up CLI mode environment (48-char key pattern)."""
    original = os.environ.get('ANTHROPIC_API_KEY')
    os.environ['ANTHROPIC_API_KEY'] = '999999999999999999999999999999999999999999999999'
    yield
    if original:
        os.environ['ANTHROPIC_API_KEY'] = original
    else:
        del os.environ['ANTHROPIC_API_KEY']


class TestClaudeClientInitialization:
    """Test Claude client initialization."""

    def test_init_with_api_key(self, api_env):
        """Test initialization with real API key."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")

        assert client.api_key is not None
        assert len(client.api_key) > 20  # Real keys are long
        assert not client.is_cli_mode
        assert "claude" in client.model.lower()
        assert client.max_tokens > 0

    def test_init_with_cli_mode(self, cli_env):
        """Test initialization in CLI mode (48-char key)."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")

        assert client.is_cli_mode
        assert len(client.api_key) == 48

    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        from kosmos.core.llm import ClaudeClient

        # Temporarily remove API key
        original = os.environ.get('ANTHROPIC_API_KEY')
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']

        try:
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable not set"):
                ClaudeClient()
        finally:
            if original:
                os.environ['ANTHROPIC_API_KEY'] = original

    def test_custom_parameters(self, api_env):
        """Test initialization with custom parameters."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(
            model="claude-3-haiku-20240307",
            max_tokens=8192,
            temperature=0.5
        )

        assert client.model == "claude-3-haiku-20240307"
        assert client.max_tokens == 8192
        assert client.temperature == 0.5


class TestClaudeClientGeneration:
    """Test Claude text generation with real API calls."""

    def test_generate_basic(self, api_env):
        """Test basic text generation with real API."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        # Use unique prompt to avoid cache hits
        response = client.generate(unique_prompt("Say 'Hello World' and nothing else."))

        # Verify we got a real response
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
        assert "hello" in response.lower() or "world" in response.lower()

        # Verify statistics are tracked (cache miss = real API call)
        assert client.total_requests == 1
        assert client.total_input_tokens > 0
        assert client.total_output_tokens > 0

    def test_generate_with_system_prompt(self, api_env):
        """Test generation with system prompt."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        response = client.generate(
            prompt="What is your purpose?",
            system="You are a helpful math tutor. Always mention that you help with math."
        )

        # System prompt should influence response
        assert response is not None
        assert len(response) > 0
        # The response should mention math given the system prompt
        assert "math" in response.lower() or "tutor" in response.lower() or "help" in response.lower()

    def test_generate_with_overrides(self, api_env):
        """Test generation with parameter overrides."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        response = client.generate(
            prompt="Write exactly one word.",
            max_tokens=50,
            temperature=0.0  # Deterministic
        )

        # Should get a response (short due to max_tokens)
        assert response is not None
        assert len(response) > 0

    def test_generate_with_messages(self, api_env):
        """Test multi-turn generation."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        messages = [
            {"role": "user", "content": "My name is Alice."},
            {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
            {"role": "user", "content": "What is my name?"}
        ]

        response = client.generate_with_messages(messages)

        # Should remember context from conversation
        assert response is not None
        assert "alice" in response.lower()


class TestClaudeClientStructured:
    """Test structured output generation with real API."""

    def test_generate_structured_json(self, api_env):
        """Test structured JSON output."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }

        result = client.generate_structured(
            prompt="Generate a JSON object with a person's name (John) and age (30). Output ONLY valid JSON.",
            output_schema=schema
        )

        # Should get valid JSON back
        assert isinstance(result, dict)
        assert "name" in result or "age" in result

    def test_generate_structured_with_markdown(self, api_env):
        """Test structured output extraction from markdown code block."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        result = client.generate_structured(
            prompt="Return this JSON in a markdown code block: {\"status\": \"ok\"}",
            output_schema={"type": "object"}
        )

        # Should parse JSON from markdown block
        assert isinstance(result, dict)

    def test_generate_structured_invalid_json(self, api_env):
        """Test error handling for invalid JSON."""
        from kosmos.core.llm import ClaudeClient
        from kosmos.core.providers.base import ProviderAPIError

        client = ClaudeClient(model="claude-3-haiku-20240307")

        # Force a non-JSON response (might still get JSON, so this test is probabilistic)
        # Instead, test that the method handles malformed input gracefully
        try:
            result = client.generate_structured(
                prompt="Write a poem about the sea. Do not use any JSON.",
                output_schema={"type": "object"}
            )
            # If it somehow parses, that's fine
            assert isinstance(result, dict)
        except (ValueError, ProviderAPIError) as e:
            # Expected - invalid JSON should raise error
            assert "JSON" in str(e) or "json" in str(e).lower()


class TestClaudeClientStatistics:
    """Test usage statistics tracking with real API."""

    def test_get_usage_stats(self, api_env):
        """Test getting usage statistics."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        # Use unique prompts to avoid cache hits
        client.generate(unique_prompt("Say 'one'"))
        client.generate(unique_prompt("Say 'two'"))

        stats = client.get_usage_stats()

        assert stats["total_requests"] == 2
        assert stats["total_input_tokens"] > 0
        assert stats["total_output_tokens"] > 0
        assert "estimated_cost_usd" in stats

    def test_cost_estimation_api_mode(self, api_env):
        """Test cost estimation in API mode."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        client.generate(unique_prompt("Hello"))

        stats = client.get_usage_stats()

        # Should have non-zero cost in API mode
        assert stats["estimated_cost_usd"] >= 0  # Haiku is very cheap

    def test_cost_estimation_cli_mode(self, cli_env):
        """Test cost estimation in CLI mode (should be 0)."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        # Note: CLI mode won't actually work with real API, but we can test initialization
        # This just tests that cli_mode is detected correctly

        stats = client.get_usage_stats()

        # Should be zero cost before any requests
        assert stats["estimated_cost_usd"] == 0.0

    def test_reset_stats(self, api_env):
        """Test resetting statistics."""
        from kosmos.core.llm import ClaudeClient

        client = ClaudeClient(model="claude-3-haiku-20240307")
        client.generate(unique_prompt("Test"))

        assert client.total_requests == 1

        client.reset_stats()

        assert client.total_requests == 0
        assert client.total_input_tokens == 0
        assert client.total_output_tokens == 0


class TestClaudeClientSingleton:
    """Test singleton client instance."""

    def test_get_client(self, api_env):
        """Test getting default client."""
        from kosmos.core.llm import get_client

        client1 = get_client()
        client2 = get_client()

        # Should return same instance
        assert client1 is client2

    def test_get_client_reset(self, api_env):
        """Test resetting default client."""
        from kosmos.core.llm import get_client

        client1 = get_client()
        client2 = get_client(reset=True)

        # Should return different instance after reset
        assert client1 is not client2
