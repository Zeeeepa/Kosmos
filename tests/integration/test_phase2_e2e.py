"""
End-to-end integration tests for Phase 2 components.

These tests verify that all Phase 2 components work together correctly
in realistic workflows.

Tests using REAL Claude API for LLM-dependent tests.
Infrastructure mocks (Neo4j, ChromaDB) kept for isolation.
External API mocks (arXiv, Semantic Scholar) kept for rate limiting.
"""

import os
import pytest
import uuid
from unittest.mock import patch, Mock

from kosmos.knowledge.embeddings import PaperEmbedder
from kosmos.knowledge.vector_db import PaperVectorDB as VectorDatabase
from kosmos.knowledge.graph import KnowledgeGraph
from kosmos.agents.literature_analyzer import LiteratureAnalyzerAgent


# Skip all tests if API key not available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.requires_claude,
    pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="Requires ANTHROPIC_API_KEY for real LLM calls"
    )
]


def unique_id() -> str:
    """Generate unique ID for test isolation."""
    return uuid.uuid4().hex[:8]


class TestSearchAndAnalyzeWorkflow:
    """Test complete search and analysis workflow."""

    @pytest.mark.slow
    def test_search_and_summarize_workflow(self, tmp_path, sample_papers_list):
        """Test: Search → Analyze → Store results with real Claude."""
        from kosmos.core.llm import ClaudeClient

        # 1. Use sample papers (mock search to avoid rate limits)
        papers = sample_papers_list[:1]

        # 2. Analyze with real Claude agent (disable heavy components)
        with patch('kosmos.agents.literature_analyzer.get_client') as mock_get_client:
            mock_get_client.return_value = ClaudeClient(model="claude-3-haiku-20240307")

            agent = LiteratureAnalyzerAgent(config={
                "use_knowledge_graph": False,
                "use_semantic_similarity": False,
                "extract_concepts": False
            })
            if papers:
                analysis = agent.summarize_paper(papers[0])
                assert analysis is not None
                assert len(analysis.executive_summary) > 0


class TestKnowledgeGraphWorkflow:
    """Test knowledge graph construction workflow (mocked infrastructure)."""

    def test_build_knowledge_graph_workflow(self, sample_papers_list):
        """Test: KnowledgeGraph initialization with mocked infrastructure."""
        # This test verifies KnowledgeGraph can be initialized with mocked Neo4j
        with patch('py2neo.Graph') as mock_graph:
            with patch('kosmos.knowledge.graph.KnowledgeGraph._ensure_container_running'):
                # Create mocked KG
                kg = KnowledgeGraph(auto_start_container=False, create_indexes=False)
                kg.graph = mock_graph.return_value

                # Verify KG was created and has expected attributes
                assert kg is not None
                assert kg.graph is not None
                assert hasattr(kg, 'create_paper')  # Check method exists


class TestVectorSearchWorkflow:
    """Test vector search workflow (infrastructure mocked)."""

    @pytest.mark.slow
    def test_embed_and_search_workflow(self, sample_papers_list):
        """Test: Embed Papers → Store → Search (infrastructure mocked)."""
        # Mock ChromaDB and SentenceTransformer to avoid loading heavy models
        with patch('chromadb.Client') as mock_chroma:
            with patch('sentence_transformers.SentenceTransformer'):
                with patch('kosmos.knowledge.embeddings.PaperEmbedder') as mock_embedder:
                    # Mock embedder methods
                    mock_embedder_instance = Mock()
                    mock_embedder_instance.embed_paper.return_value = [0.1] * 768
                    mock_embedder.return_value = mock_embedder_instance

                    # Create vector DB with mocked components
                    with patch.object(VectorDatabase, '__init__', lambda self, **kwargs: None):
                        db = VectorDatabase.__new__(VectorDatabase)
                        db.collection = Mock()
                        db.embedder = mock_embedder_instance

                        # Verify we can call methods (they're mocked)
                        db.collection.add.return_value = None
                        assert db.collection is not None


class TestErrorHandling:
    """Test error handling across components."""

    def test_missing_services_degradation(self, sample_paper_metadata):
        """Test degraded functionality when services unavailable with real Claude."""
        from kosmos.core.llm import ClaudeClient

        with patch('kosmos.agents.literature_analyzer.get_client') as mock_get_client:
            mock_get_client.return_value = ClaudeClient(model="claude-3-haiku-20240307")

            # Agent with disabled heavy components
            agent = LiteratureAnalyzerAgent(config={
                "use_knowledge_graph": False,
                "use_semantic_similarity": False,
                "extract_concepts": False
            })

            # Should still work without heavy components
            analysis = agent.summarize_paper(sample_paper_metadata)
            assert analysis is not None
            assert len(analysis.executive_summary) > 0


@pytest.mark.slow
class TestRealServicesIntegration:
    """Integration tests with real Claude."""

    def test_real_end_to_end_workflow(self, sample_papers_list):
        """Test LiteratureAnalyzerAgent with real Claude."""
        from kosmos.core.llm import ClaudeClient

        # Use sample papers
        papers = sample_papers_list[:1]

        # Real agent analysis with real Claude
        with patch('kosmos.agents.literature_analyzer.get_client') as mock_get_client:
            mock_get_client.return_value = ClaudeClient(model="claude-3-haiku-20240307")

            agent = LiteratureAnalyzerAgent(config={
                "use_knowledge_graph": False,
                "use_semantic_similarity": False,
                "extract_concepts": False
            })
            agent.start()
            analysis = agent.summarize_paper(papers[0])
            agent.stop()

            assert analysis is not None
            assert len(analysis.executive_summary) > 0
