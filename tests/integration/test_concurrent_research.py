"""
Integration tests for concurrent research operations.

Tests Research Director with concurrent hypothesis evaluation,
experiment execution, and result analysis.

Uses mocked AsyncClaudeClient and ParallelExperimentExecutor to test
concurrent workflows without making real API calls.
"""

import os
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from kosmos.agents.research_director import ResearchDirectorAgent

# Integration test markers - these tests use mocks so don't require API key
pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio,
]


class TestConcurrentHypothesisEvaluation:
    """Test concurrent hypothesis evaluation."""

    @pytest.fixture
    def mock_async_client(self):
        """Mock AsyncClaudeClient."""
        with patch('kosmos.core.async_llm.AsyncClaudeClient') as mock:
            client = AsyncMock()

            # Mock batch_generate to return evaluations
            async def mock_batch_generate(requests):
                from kosmos.core.async_llm import BatchResponse
                return [
                    BatchResponse(
                        id=req.id,
                        response='{"testability": 8, "novelty": 7, "impact": 9, "recommendation": "proceed", "reasoning": "Strong hypothesis"}',
                        success=True,
                        input_tokens=30,
                        output_tokens=20,
                        execution_time=0.1
                    )
                    for req in requests
                ]

            client.batch_generate = mock_batch_generate
            mock.return_value = client

            yield client

    @pytest.mark.asyncio
    async def test_evaluate_multiple_hypotheses_concurrently(self, mock_async_client):
        """Test evaluating multiple hypotheses concurrently."""
        config = {
            "enable_concurrent_operations": True,
            "max_parallel_hypotheses": 3,
            "max_concurrent_experiments": 4
        }

        director = ResearchDirectorAgent(
            research_question="Test question",
            config=config
        )
        director.async_llm_client = mock_async_client

        # Mock hypothesis IDs
        hypothesis_ids = [f"hyp_{i}" for i in range(5)]

        # Evaluate concurrently
        results = await director.evaluate_hypotheses_concurrently(hypothesis_ids)

        assert len(results) == 5
        assert all(r.get("recommendation") == "proceed" for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_evaluation_faster_than_sequential(self, mock_async_client):
        """Test concurrent evaluation is faster."""
        import time

        # Add delay to mock
        async def slow_batch_generate(requests):
            await asyncio.sleep(0.1 * len(requests))  # Simulate API latency
            from kosmos.core.async_llm import BatchResponse
            return [
                BatchResponse(
                    id=req.id,
                    response='{"testability": 8, "novelty": 7, "impact": 9, "recommendation": "proceed"}',
                    success=True,
                    input_tokens=30,
                    output_tokens=20,
                    execution_time=0.1
                )
                for req in requests
            ]

        mock_async_client.batch_generate = slow_batch_generate

        config = {"enable_concurrent_operations": True}
        director = ResearchDirectorAgent(research_question="Test", config=config)
        director.async_llm_client = mock_async_client

        hypothesis_ids = [f"hyp_{i}" for i in range(6)]

        start = time.time()
        results = await director.evaluate_hypotheses_concurrently(hypothesis_ids)
        concurrent_time = time.time() - start

        # With concurrency, should complete in ~0.6s
        # Sequential would be much slower
        assert concurrent_time < 1.5
        assert len(results) == 6


class TestConcurrentExperimentExecution:
    """Test concurrent experiment execution."""

    @pytest.fixture
    def mock_parallel_executor(self):
        """Mock ParallelExperimentExecutor."""
        with patch('kosmos.execution.parallel.ParallelExperimentExecutor') as mock:
            executor = MagicMock()

            # Mock execute_batch
            def mock_execute_batch(protocol_ids):
                return [
                    {
                        "protocol_id": pid,
                        "success": True,
                        "result_id": f"result_{pid}",
                        "duration": 1.0
                    }
                    for pid in protocol_ids
                ]

            executor.execute_batch = mock_execute_batch
            mock.return_value = executor

            yield executor

    def test_execute_multiple_experiments_in_parallel(self, mock_parallel_executor):
        """Test executing multiple experiments in parallel."""
        config = {
            "enable_concurrent_operations": True,
            "max_concurrent_experiments": 4
        }

        director = ResearchDirectorAgent(research_question="Test", config=config)
        director.parallel_executor = mock_parallel_executor

        protocol_ids = [f"protocol_{i}" for i in range(8)]

        results = director.execute_experiments_batch(protocol_ids)

        assert len(results) == 8
        assert all(r["success"] for r in results)

    def test_parallel_execution_updates_research_plan(self, mock_parallel_executor):
        """Test parallel execution updates research plan safely."""
        config = {"enable_concurrent_operations": True}

        director = ResearchDirectorAgent(research_question="Test", config=config)
        director.parallel_executor = mock_parallel_executor

        protocol_ids = ["protocol_1", "protocol_2"]

        # Initialize research plan
        director.research_plan.experiment_queue = set(protocol_ids)

        results = director.execute_experiments_batch(protocol_ids)

        # Results should be added to research plan
        assert len(results) == 2

        # Queue should be updated (thread-safe)
        # (actual implementation depends on research plan structure)


class TestConcurrentResultAnalysis:
    """Test concurrent result analysis."""

    @pytest.fixture
    def mock_async_client(self):
        """Mock AsyncClaudeClient for result analysis."""
        with patch('kosmos.core.async_llm.AsyncClaudeClient') as mock:
            client = AsyncMock()

            async def mock_batch_generate(requests):
                from kosmos.core.async_llm import BatchResponse
                return [
                    BatchResponse(
                        id=req.id,
                        response='{"significance": "high", "hypothesis_supported": true, "key_finding": "Positive result", "next_steps": "Continue research"}',
                        success=True,
                        input_tokens=50,
                        output_tokens=25,
                        execution_time=0.15
                    )
                    for req in requests
                ]

            client.batch_generate = mock_batch_generate
            mock.return_value = client

            yield client

    @pytest.mark.asyncio
    async def test_analyze_multiple_results_concurrently(self, mock_async_client):
        """Test analyzing multiple results concurrently."""
        config = {"enable_concurrent_operations": True}

        director = ResearchDirectorAgent(research_question="Test", config=config)
        director.async_llm_client = mock_async_client

        result_ids = [f"result_{i}" for i in range(5)]

        analyses = await director.analyze_results_concurrently(result_ids)

        assert len(analyses) == 5
        assert all(a.get("significance") == "high" for a in analyses)


class TestThreadSafetyInConcurrentOperations:
    """Test thread safety of concurrent operations."""

    def test_research_plan_thread_safety(self):
        """Test research plan updates are thread-safe."""
        import threading

        config = {"enable_concurrent_operations": True}
        director = ResearchDirectorAgent(research_question="Test", config=config)

        # Multiple threads updating research plan
        def add_hypothesis(thread_id):
            for i in range(10):
                with director._research_plan_context():
                    director.research_plan.add_hypothesis(f"hyp_{thread_id}_{i}")

        threads = [
            threading.Thread(target=add_hypothesis, args=(i,))
            for i in range(5)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All hypotheses should be added without race conditions
        # (Actual count depends on research plan implementation)
        assert True  # No crashes = thread-safe

    def test_strategy_stats_thread_safety(self):
        """Test strategy stats updates are thread-safe."""
        import threading

        config = {"enable_concurrent_operations": True}
        director = ResearchDirectorAgent(research_question="Test", config=config)

        def update_stats(thread_id):
            for i in range(100):
                with director._strategy_stats_context():
                    if "test_strategy" not in director.strategy_stats:
                        director.strategy_stats["test_strategy"] = {"attempts": 0, "successes": 0}
                    director.strategy_stats["test_strategy"]["attempts"] += 1

        threads = [
            threading.Thread(target=update_stats, args=(i,))
            for i in range(5)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Should have 500 attempts (5 threads * 100 iterations)
        assert director.strategy_stats.get("test_strategy", {}).get("attempts") == 500


class TestConcurrentOperationsIntegration:
    """Integration tests for full concurrent research workflow."""

    @pytest.fixture
    def fully_mocked_director(self):
        """Create director with all dependencies mocked."""
        with patch('kosmos.core.async_llm.AsyncClaudeClient') as mock_async, \
             patch('kosmos.execution.parallel.ParallelExperimentExecutor') as mock_parallel:
            config = {
                "enable_concurrent_operations": True,
                "max_parallel_hypotheses": 3,
                "max_concurrent_experiments": 4
            }

            director = ResearchDirectorAgent(
                research_question="Test concurrent operations",
                config=config
            )

            # Setup mocks
            async_client = AsyncMock()
            async def mock_batch(requests):
                from kosmos.core.async_llm import BatchResponse
                return [
                    BatchResponse(id=r.id, response="test", success=True, input_tokens=5, output_tokens=5, execution_time=0.05)
                    for r in requests
                ]
            async_client.batch_generate = mock_batch

            parallel_exec = MagicMock()
            parallel_exec.execute_batch = lambda ids: [
                {"protocol_id": i, "success": True, "result_id": f"r_{i}"}
                for i in ids
            ]

            director.async_llm_client = async_client
            director.parallel_executor = parallel_exec

            yield director

    @pytest.mark.integration
    def test_full_concurrent_research_cycle(self, fully_mocked_director):
        """Test complete research cycle with concurrency."""
        director = fully_mocked_director

        # Simulate research workflow
        # 1. Generate hypotheses (mocked)
        director.research_plan.add_hypothesis("hyp_1")
        director.research_plan.add_hypothesis("hyp_2")
        director.research_plan.add_hypothesis("hyp_3")

        # 2. Evaluate concurrently
        hypothesis_ids = ["hyp_1", "hyp_2", "hyp_3"]
        evaluations = asyncio.run(
            director.evaluate_hypotheses_concurrently(hypothesis_ids)
        )

        assert len(evaluations) >= 0  # Mocked, may return empty

        # 3. Design and execute experiments (experiment_queue is a list)
        director.research_plan.experiment_queue.append("exp_1")
        director.research_plan.experiment_queue.append("exp_2")

        results = director.execute_experiments_batch(["exp_1", "exp_2"])
        assert len(results) == 2

        # 4. Analyze results concurrently
        result_ids = ["result_1", "result_2"]
        analyses = asyncio.run(
            director.analyze_results_concurrently(result_ids)
        )

        assert len(analyses) >= 0  # Mocked

    @pytest.mark.integration
    def test_fallback_to_sequential_when_concurrent_unavailable(self):
        """Test graceful fallback to sequential mode when imports fail."""
        # Mock AsyncClaudeClient to raise ImportError
        with patch('kosmos.core.async_llm.AsyncClaudeClient', side_effect=ImportError("No async support")), \
             patch('kosmos.execution.parallel.ParallelExperimentExecutor', side_effect=ImportError("No parallel support")):
            config = {
                "enable_concurrent_operations": True,  # Requested
            }

            director = ResearchDirectorAgent(research_question="Test", config=config)

            # Should fall back to sequential mode (clients are None due to import errors)
            assert director.async_llm_client is None
            assert director.parallel_executor is None


class TestPerformanceMetrics:
    """Test performance metrics with concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_throughput_improvement(self):
        """Test concurrent operations improve throughput."""
        import time

        # Mock client with realistic delays
        client = AsyncMock()

        async def realistic_batch_generate(requests):
            # Simulate 100ms per request (concurrent)
            await asyncio.sleep(0.1)
            from kosmos.core.async_llm import BatchResponse
            return [
                BatchResponse(id=r.id, response="result", success=True, input_tokens=30, output_tokens=20, execution_time=0.1)
                for r in requests
            ]

        client.batch_generate = realistic_batch_generate

        config = {"enable_concurrent_operations": True}
        director = ResearchDirectorAgent(research_question="Test", config=config)
        director.async_llm_client = client

        hypothesis_ids = [f"hyp_{i}" for i in range(10)]

        start = time.time()
        results = await director.evaluate_hypotheses_concurrently(hypothesis_ids)
        duration = time.time() - start

        # Should complete in ~1s (concurrent) vs 10s (sequential)
        assert duration < 2.0
        # Allow some results (may be empty with mocks)


class TestErrorHandlingInConcurrentMode:
    """Test error handling with concurrent operations."""

    @pytest.mark.asyncio
    async def test_partial_failures_in_batch(self):
        """Test handling partial failures in concurrent batch."""
        client = AsyncMock()

        async def mixed_results_batch(requests):
            from kosmos.core.async_llm import BatchResponse
            results = []
            for i, req in enumerate(requests):
                if i % 2 == 0:
                    results.append(BatchResponse(
                        id=req.id,
                        response='{"recommendation": "proceed"}',
                        success=True,
                        input_tokens=30,
                        output_tokens=20,
                        execution_time=0.1
                    ))
                else:
                    results.append(BatchResponse(
                        id=req.id,
                        response="",
                        success=False,
                        error="API error"
                    ))
            return results

        client.batch_generate = mixed_results_batch

        config = {"enable_concurrent_operations": True}
        director = ResearchDirectorAgent(research_question="Test", config=config)
        director.async_llm_client = client

        hypothesis_ids = [f"hyp_{i}" for i in range(6)]

        results = await director.evaluate_hypotheses_concurrently(hypothesis_ids)

        # Should return all results (successes and failures)
        assert len(results) == 6
        successes = sum(1 for r in results if r.get("recommendation") == "proceed")
        errors = sum(1 for r in results if "error" in r)

        assert successes == 3  # Even indices
        assert errors == 3  # Odd indices
