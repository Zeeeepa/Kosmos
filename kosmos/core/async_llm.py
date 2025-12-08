"""
Async LLM client for concurrent Claude API calls.

Provides async/await wrapper around the Anthropic API for concurrent operations,
batch processing, and rate-limited concurrent requests.
"""

import asyncio
import logging
import time
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from kosmos.config import _DEFAULT_CLAUDE_SONNET_MODEL

try:
    from anthropic import AsyncAnthropic, APIError, APITimeoutError, RateLimitError
    ASYNC_ANTHROPIC_AVAILABLE = True
except ImportError:
    ASYNC_ANTHROPIC_AVAILABLE = False
    # Create unique placeholder classes so isinstance() checks don't match unrelated exceptions
    class APIError(Exception):
        """Placeholder for anthropic.APIError when package not installed."""
        pass
    class APITimeoutError(Exception):
        """Placeholder for anthropic.APITimeoutError when package not installed."""
        pass
    class RateLimitError(Exception):
        """Placeholder for anthropic.RateLimitError when package not installed."""
        pass

# Import retry decorator
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

from kosmos.core.providers.base import ProviderAPIError

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern for LLM API calls.

    Prevents cascading failures by stopping requests after consecutive failures.
    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        reset_timeout: float = 60.0,
        half_open_max_calls: int = 1
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"
        self.half_open_calls = 0
        self._lock = asyncio.Lock()

    async def can_execute(self) -> bool:
        """Check if a request can be executed."""
        async with self._lock:
            if self.state == "CLOSED":
                return True

            if self.state == "OPEN":
                # Check if reset timeout has passed
                if self.last_failure_time and \
                   time.time() - self.last_failure_time >= self.reset_timeout:
                    self.state = "HALF_OPEN"
                    self.half_open_calls = 0
                    logger.info("Circuit breaker entering HALF_OPEN state")
                    return True
                return False

            if self.state == "HALF_OPEN":
                # Allow limited calls in half-open state
                if self.half_open_calls < self.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False

            return False

    async def record_success(self):
        """Record a successful request."""
        async with self._lock:
            self.failure_count = 0
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                logger.info("Circuit breaker CLOSED after successful request")

    async def record_failure(self, error: Exception):
        """Record a failed request."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == "HALF_OPEN":
                # Immediate open on failure in half-open state
                self.state = "OPEN"
                logger.warning("Circuit breaker re-OPENED after failure in HALF_OPEN state")
            elif self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning(
                    f"Circuit breaker OPENED after {self.failure_count} consecutive failures"
                )

    def is_open(self) -> bool:
        """Check if circuit breaker is open (blocking requests)."""
        return self.state == "OPEN"

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state info."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
        }


def is_recoverable_error(error: Exception) -> bool:
    """
    Check if an error is recoverable (worth retrying).

    Args:
        error: The exception to check

    Returns:
        True if error might succeed on retry
    """
    # Check ProviderAPIError's recoverable flag
    if isinstance(error, ProviderAPIError):
        return error.is_recoverable()

    # Anthropic SDK errors
    if isinstance(error, RateLimitError):
        return True  # Always retry rate limits
    if isinstance(error, APITimeoutError):
        return True  # Network timeouts are recoverable
    if isinstance(error, APIError):
        # Check error message for hints
        error_str = str(error).lower()
        non_recoverable = ['invalid', 'authentication', 'unauthorized', 'forbidden']
        if any(term in error_str for term in non_recoverable):
            return False
        return True  # Default to recoverable for API errors

    # Default: unknown errors are potentially recoverable
    return True


@dataclass
class BatchRequest:
    """Single request in a batch."""
    id: str
    prompt: str
    system: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model_override: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchResponse:
    """Response for a single batch request."""
    id: str
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    execution_time: float = 0.0

    @property
    def tokens_used(self) -> int:
        """Total tokens (input + output) for compatibility."""
        return self.input_tokens + self.output_tokens

    @property
    def latency_ms(self) -> float:
        """Execution time in milliseconds for compatibility."""
        return self.execution_time * 1000


class RateLimiter:
    """
    Token bucket rate limiter for async operations.

    Ensures we don't exceed API rate limits by controlling
    the rate of concurrent requests.
    """

    def __init__(
        self,
        max_requests_per_minute: int = 50,
        max_concurrent: int = 5
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_minute: Maximum requests per minute
            max_concurrent: Maximum concurrent requests
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.max_concurrent = max_concurrent

        # Semaphore for concurrent requests
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Token bucket for rate limiting
        self.tokens = max_requests_per_minute
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make a request."""
        # Wait for concurrent slot
        await self.semaphore.acquire()

        # Wait for rate limit token
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Refill tokens based on elapsed time
            tokens_to_add = elapsed * (self.max_requests_per_minute / 60.0)
            self.tokens = min(
                self.max_requests_per_minute,
                self.tokens + tokens_to_add
            )
            self.last_update = now

            # If no tokens available, wait
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / (self.max_requests_per_minute / 60.0)
                await asyncio.sleep(wait_time)
                self.tokens = 1

            # Consume token
            self.tokens -= 1

    def release(self):
        """Release concurrent slot."""
        self.semaphore.release()


class AsyncClaudeClient:
    """
    Async wrapper for Claude API enabling concurrent operations.

    Provides async/await interface for non-blocking Claude API calls,
    batch processing, and rate-limited concurrent execution.

    Example:
        ```python
        client = AsyncClaudeClient(api_key="your-key")

        # Single async call
        response = await client.async_generate(
            prompt="Explain quantum computing",
            system="You are a physics professor"
        )

        # Batch processing
        requests = [
            BatchRequest(id="1", prompt="What is AI?"),
            BatchRequest(id="2", prompt="What is ML?"),
        ]
        responses = await client.batch_generate(requests)

        # Concurrent generation
        prompts = ["Question 1", "Question 2", "Question 3"]
        responses = await client.concurrent_generate(prompts, system="You are helpful")
        ```
    """

    def __init__(
        self,
        api_key: str,
        model: str = _DEFAULT_CLAUDE_SONNET_MODEL,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        max_concurrent: int = 5,
        max_requests_per_minute: int = 50,
        enable_cache: bool = False,
        cache: Optional[Any] = None
    ):
        """
        Initialize async Claude client.

        Args:
            api_key: Anthropic API key
            model: Default Claude model
            max_tokens: Default max tokens
            temperature: Default temperature
            max_concurrent: Maximum concurrent requests (default: 5)
            max_requests_per_minute: Rate limit (default: 50)
            enable_cache: Enable response caching
            cache: Optional cache instance
        """
        if not ASYNC_ANTHROPIC_AVAILABLE:
            raise ImportError(
                "AsyncAnthropic not available. "
                "Install with: pip install anthropic[async]"
            )

        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.enable_cache = enable_cache
        self.cache = cache

        # Initialize async client
        self.client = AsyncAnthropic(api_key=api_key)

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests_per_minute=max_requests_per_minute,
            max_concurrent=max_concurrent
        )

        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            reset_timeout=60.0
        )

        # Statistics
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.failed_requests = 0

        logger.info(
            f"Async Claude client initialized "
            f"(max_concurrent={max_concurrent}, "
            f"rate_limit={max_requests_per_minute}/min)"
        )

    async def async_generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        model_override: Optional[str] = None,
        bypass_cache: bool = False
    ) -> str:
        """
        Generate text asynchronously from Claude.

        Args:
            prompt: The user prompt/question
            system: Optional system prompt
            max_tokens: Override default max_tokens
            temperature: Override default temperature
            stop_sequences: Optional list of stop sequences
            model_override: Override default model
            bypass_cache: Force bypass cache

        Returns:
            Generated text from Claude

        Example:
            ```python
            response = await client.async_generate(
                prompt="Explain neural networks",
                system="You are an AI expert"
            )
            ```
        """
        # Check cache first
        if self.enable_cache and self.cache and not bypass_cache:
            cached = self.cache.get(
                prompt=prompt,
                model=model_override or self.model,
                system=system or "",
                bypass=False
            )
            if cached:
                logger.debug("Cache hit for async request")
                return cached['response']

        # Check circuit breaker before proceeding
        if not await self.circuit_breaker.can_execute():
            logger.warning("Circuit breaker is OPEN, request blocked")
            raise ProviderAPIError(
                "anthropic",
                "Circuit breaker is open - too many consecutive failures",
                recoverable=True  # Will be retryable after timeout
            )

        # Acquire rate limit
        await self.rate_limiter.acquire()
        start_time = time.time()

        # Define timeout (2 minutes default)
        timeout_seconds = 120

        try:
            # Build message
            messages = [{"role": "user", "content": prompt}]

            # Custom retry predicate that checks recoverability
            def should_retry(retry_state):
                """Only retry recoverable errors."""
                if retry_state.outcome.failed:
                    error = retry_state.outcome.exception()
                    recoverable = is_recoverable_error(error)
                    if not recoverable:
                        logger.info(f"Not retrying non-recoverable error: {error}")
                    return recoverable
                return False

            # Call Claude API with timeout and retry logic
            async def _api_call_with_retry():
                """Inner function with retry decorator."""
                # Apply retry logic if tenacity is available
                if TENACITY_AVAILABLE:
                    @retry(
                        stop=stop_after_attempt(3),
                        wait=wait_exponential(multiplier=1, min=2, max=30),
                        retry=should_retry,  # Use custom predicate
                        before_sleep=before_sleep_log(logger, logging.WARNING),
                        reraise=True
                    )
                    async def _call():
                        return await self.client.messages.create(
                            model=model_override or self.model,
                            max_tokens=max_tokens or self.max_tokens,
                            temperature=temperature or self.temperature,
                            system=system or "",
                            messages=messages,
                            stop_sequences=stop_sequences or []
                        )
                    return await _call()
                else:
                    # No retry if tenacity not available
                    return await self.client.messages.create(
                        model=model_override or self.model,
                        max_tokens=max_tokens or self.max_tokens,
                        temperature=temperature or self.temperature,
                        system=system or "",
                        messages=messages,
                        stop_sequences=stop_sequences or []
                    )

            # Execute with timeout
            try:
                response = await asyncio.wait_for(
                    _api_call_with_retry(),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"LLM API call timed out after {timeout_seconds}s")
                await self.circuit_breaker.record_failure(APITimeoutError("timeout"))
                raise APITimeoutError(f"API call exceeded timeout of {timeout_seconds}s")

            # Update statistics
            self.total_requests += 1
            if hasattr(response, 'usage'):
                self.total_input_tokens += response.usage.input_tokens
                self.total_output_tokens += response.usage.output_tokens

            # Extract text
            text = response.content[0].text

            # Cache response
            if self.enable_cache and self.cache and not bypass_cache:
                metadata = {}
                if hasattr(response, 'usage'):
                    metadata = {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens,
                    }
                self.cache.set(
                    prompt=prompt,
                    model=model_override or self.model,
                    response=text,
                    system=system or "",
                    metadata=metadata
                )

            execution_time = time.time() - start_time
            logger.debug(
                f"Async generation completed in {execution_time:.2f}s "
                f"({len(text)} chars)"
            )

            # Record success with circuit breaker
            await self.circuit_breaker.record_success()

            return text

        except (APIError, APITimeoutError, RateLimitError, ProviderAPIError) as e:
            self.failed_requests += 1
            await self.circuit_breaker.record_failure(e)
            logger.error(f"Async generation failed after retries: {e}")
            raise
        except Exception as e:
            self.failed_requests += 1
            await self.circuit_breaker.record_failure(e)
            logger.error(f"Async generation failed: {e}")
            raise

        finally:
            self.rate_limiter.release()

    async def batch_generate(
        self,
        requests: List[BatchRequest]
    ) -> List[BatchResponse]:
        """
        Process multiple requests concurrently.

        Args:
            requests: List of BatchRequest objects

        Returns:
            List of BatchResponse objects in the same order as requests

        Example:
            ```python
            requests = [
                BatchRequest(id="1", prompt="What is AI?"),
                BatchRequest(id="2", prompt="What is ML?", system="Expert mode"),
                BatchRequest(id="3", prompt="What is DL?"),
            ]
            responses = await client.batch_generate(requests)
            for resp in responses:
                print(f"{resp.id}: {resp.response}")
            ```
        """
        logger.info(f"Processing batch of {len(requests)} requests")

        # Create tasks for all requests
        tasks = [
            self._process_single_batch_request(req)
            for req in requests
        ]

        # Execute concurrently and wait for all
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error responses
        final_responses = []
        for i, result in enumerate(responses):
            if isinstance(result, Exception):
                final_responses.append(BatchResponse(
                    id=requests[i].id,
                    success=False,
                    error=str(result)
                ))
            else:
                final_responses.append(result)

        successful = sum(1 for r in final_responses if r.success)
        logger.info(
            f"Batch completed: {successful}/{len(requests)} successful"
        )

        return final_responses

    async def _process_single_batch_request(
        self,
        request: BatchRequest
    ) -> BatchResponse:
        """Process a single batch request."""
        start_time = time.time()

        try:
            response = await self.async_generate(
                prompt=request.prompt,
                system=request.system,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                model_override=request.model_override
            )

            execution_time = time.time() - start_time

            return BatchResponse(
                id=request.id,
                success=True,
                response=response,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return BatchResponse(
                id=request.id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )

    async def concurrent_generate(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> List[str]:
        """
        Generate responses for multiple prompts concurrently.

        Args:
            prompts: List of prompts
            system: System prompt (same for all)
            max_tokens: Max tokens (same for all)
            temperature: Temperature (same for all)

        Returns:
            List of responses in the same order as prompts

        Example:
            ```python
            prompts = [
                "What is Python?",
                "What is JavaScript?",
                "What is Rust?"
            ]
            responses = await client.concurrent_generate(
                prompts,
                system="You are a programming expert"
            )
            for prompt, response in zip(prompts, responses):
                print(f"Q: {prompt}")
                print(f"A: {response}\n")
            ```
        """
        # Create batch requests
        requests = [
            BatchRequest(
                id=str(i),
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature
            )
            for i, prompt in enumerate(prompts)
        ]

        # Process batch
        responses = await self.batch_generate(requests)

        # Extract response text (maintain order, use empty string for failures)
        return [
            resp.response if resp.success else ""
            for resp in responses
        ]

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics.

        Returns:
            Dictionary with usage metrics
        """
        return {
            'total_requests': self.total_requests,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'failed_requests': self.failed_requests,
            'success_rate': (
                (self.total_requests - self.failed_requests) / self.total_requests * 100
                if self.total_requests > 0 else 0
            ),
            'average_input_tokens': (
                self.total_input_tokens / self.total_requests
                if self.total_requests > 0 else 0
            ),
            'average_output_tokens': (
                self.total_output_tokens / self.total_requests
                if self.total_requests > 0 else 0
            )
        }

    async def close(self):
        """Close the async client."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Convenience function for quick async generation
async def async_generate_text(
    prompt: str,
    api_key: str,
    system: Optional[str] = None,
    model: str = _DEFAULT_CLAUDE_SONNET_MODEL,
    max_tokens: int = 4096,
    temperature: float = 0.7
) -> str:
    """
    Quick async text generation without creating a client.

    Args:
        prompt: Prompt text
        api_key: Anthropic API key
        system: Optional system prompt
        model: Claude model to use
        max_tokens: Maximum tokens
        temperature: Temperature

    Returns:
        Generated text

    Example:
        ```python
        response = await async_generate_text(
            prompt="What is quantum computing?",
            api_key="your-key",
            system="You are a physics expert"
        )
        ```
    """
    async with AsyncClaudeClient(
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    ) as client:
        return await client.async_generate(
            prompt=prompt,
            system=system
        )
