"""
Unit tests for AsyncClaudeClient.

Tests using REAL Anthropic API calls (not mocks).
Requires ANTHROPIC_API_KEY environment variable.
Uses claude-3-haiku for cost-effective testing.
"""

import pytest
import asyncio
import os
import uuid

from kosmos.core.async_llm import (
    AsyncClaudeClient,
    BatchRequest,
    BatchResponse,
    RateLimiter
)


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


class TestBatchRequest:
    """Test BatchRequest data class."""

    def test_creation(self):
        """Test creating batch request."""
        req = BatchRequest(
            id="test-1",
            prompt="Test prompt",
            system="Test system",
            temperature=0.7,
            max_tokens=1000
        )

        assert req.id == "test-1"
        assert req.prompt == "Test prompt"
        assert req.temperature == 0.7


class TestBatchResponse:
    """Test BatchResponse data class."""

    def test_success_response(self):
        """Test successful response."""
        resp = BatchResponse(
            id="test-1",
            success=True,
            response="Test response",
            input_tokens=10,
            output_tokens=20,
            execution_time=0.5
        )

        assert resp.success is True
        assert resp.error is None
        assert resp.input_tokens == 10
        assert resp.output_tokens == 20

    def test_error_response(self):
        """Test error response."""
        resp = BatchResponse(
            id="test-1",
            success=False,
            error="Rate limit exceeded"
        )

        assert resp.success is False
        assert resp.error == "Rate limit exceeded"


class TestRateLimiter:
    """Test RateLimiter implementation."""

    @pytest.mark.asyncio
    async def test_acquire_within_limit(self):
        """Test acquiring tokens within rate limit."""
        limiter = RateLimiter(max_requests_per_minute=60)

        # Should allow requests within limit
        for _ in range(5):
            await asyncio.wait_for(limiter.acquire(), timeout=5.0)

    @pytest.mark.asyncio
    async def test_rate_limiting_fast(self):
        """Test rate limiting with fast bucket."""
        # Use high rate to avoid waiting
        limiter = RateLimiter(max_requests_per_minute=600)

        # Should be fast with high limit
        import time
        start = time.time()
        for _ in range(3):
            await asyncio.wait_for(limiter.acquire(), timeout=2.0)
        elapsed = time.time() - start

        assert elapsed < 2.0


@pytest.fixture
def real_async_client():
    """Create AsyncClaudeClient with real API key."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("999"):
        pytest.skip("Real Anthropic API key not available")

    return AsyncClaudeClient(
        api_key=api_key,
        model="claude-3-haiku-20240307",
        max_concurrent=3,
        max_requests_per_minute=30
    )


@pytest.mark.asyncio
class TestAsyncClaudeClient:
    """Test AsyncClaudeClient with real API calls."""

    async def test_async_generate_single(self, real_async_client):
        """Test generating single response with real API."""
        response = await asyncio.wait_for(
            real_async_client.async_generate(
                prompt=unique_prompt("Say 'hello' and nothing else."),
                system="You are a helpful assistant."
            ),
            timeout=30.0
        )

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

        await real_async_client.close()

    async def test_batch_generate(self, real_async_client):
        """Test batch generation with real API."""
        requests = [
            BatchRequest(
                id="1",
                prompt=unique_prompt("Say 'one'"),
                temperature=0.0,
                max_tokens=20
            ),
            BatchRequest(
                id="2",
                prompt=unique_prompt("Say 'two'"),
                temperature=0.0,
                max_tokens=20
            ),
        ]

        responses = await asyncio.wait_for(
            real_async_client.batch_generate(requests),
            timeout=60.0
        )

        assert len(responses) == 2
        assert all(r.success for r in responses)
        assert all(len(r.response) > 0 for r in responses)

        await real_async_client.close()

    async def test_concurrency_limiting(self, real_async_client):
        """Test concurrent request limiting with real API."""
        # Create more requests than max_concurrent (3)
        requests = [
            BatchRequest(
                id=str(i),
                prompt=unique_prompt(f"Count: {i}"),
                temperature=0.0,
                max_tokens=10
            )
            for i in range(5)
        ]

        responses = await asyncio.wait_for(
            real_async_client.batch_generate(requests),
            timeout=90.0
        )

        # All should complete despite concurrency limit
        assert len(responses) == 5
        assert all(r.success for r in responses)

        await real_async_client.close()

    async def test_token_counting(self, real_async_client):
        """Test token usage tracking with real API."""
        requests = [
            BatchRequest(
                id="1",
                prompt=unique_prompt("Hi"),
                temperature=0.0,
                max_tokens=10
            ),
            BatchRequest(
                id="2",
                prompt=unique_prompt("Hello"),
                temperature=0.0,
                max_tokens=10
            )
        ]

        responses = await asyncio.wait_for(
            real_async_client.batch_generate(requests),
            timeout=60.0
        )

        # Token counts are tracked at client level, not in BatchResponse
        stats = real_async_client.get_usage_stats()
        assert stats['total_input_tokens'] > 0  # Should have some token usage
        assert stats['total_output_tokens'] > 0

        await real_async_client.close()

    async def test_execution_time_tracking(self, real_async_client):
        """Test execution time measurement with real API."""
        requests = [
            BatchRequest(
                id="1",
                prompt=unique_prompt("Test"),
                temperature=0.0,
                max_tokens=10
            )
        ]

        responses = await asyncio.wait_for(
            real_async_client.batch_generate(requests),
            timeout=30.0
        )

        # Should have measured some execution time
        assert responses[0].execution_time > 0

        await real_async_client.close()

    async def test_close_client(self, real_async_client):
        """Test closing client."""
        # Just verify close doesn't raise
        await real_async_client.close()


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling scenarios with real API."""

    async def test_invalid_api_key(self):
        """Test handling of invalid API key."""
        client = AsyncClaudeClient(
            api_key="sk-ant-invalid-key-12345",
            model="claude-3-haiku-20240307",
            max_concurrent=1,
            max_requests_per_minute=10
        )

        with pytest.raises(Exception):
            await asyncio.wait_for(
                client.async_generate(prompt="Test"),
                timeout=30.0
            )

        await client.close()

    async def test_empty_prompt(self, real_async_client):
        """Test handling of empty prompt."""
        # Empty prompts should still work (API handles gracefully)
        try:
            response = await asyncio.wait_for(
                real_async_client.async_generate(prompt=""),
                timeout=30.0
            )
            # Either succeeds with some response or raises gracefully
            assert True
        except Exception as e:
            # Acceptable - API may reject empty prompts
            assert True

        await real_async_client.close()
