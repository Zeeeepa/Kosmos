# Mock Tests Migration Plan: From Mocks to Real-World Tests

This document identifies all tests in the Kosmos codebase that use mock implementations and provides a detailed migration plan to replace them with real-world integration tests.

## Executive Summary

- **Total Test Files with Mocks**: 115+
- **Primary Mocking Framework**: `unittest.mock` (Mock, MagicMock, AsyncMock, patch)
- **Key Components Being Mocked**: Claude API, Neo4j, ChromaDB, External APIs (arXiv, PubMed, Semantic Scholar)

---

## Table of Contents

1. [Shared Mock Fixtures (conftest.py)](#1-shared-mock-fixtures-conftestpy)
2. [Unit Tests with Mocks](#2-unit-tests-with-mocks)
3. [Integration Tests with Mocks](#3-integration-tests-with-mocks)
4. [E2E Tests with Mocks](#4-e2e-tests-with-mocks)
5. [Requirements Tests with Mocks](#5-requirements-tests-with-mocks)
6. [Migration Strategy](#6-migration-strategy)
7. [Implementation Checklist](#7-implementation-checklist)

---

## 1. Shared Mock Fixtures (conftest.py)

**File**: `tests/conftest.py`

### Current Mock Fixtures

| Fixture Name | What It Mocks | Lines |
|-------------|---------------|-------|
| `mock_llm_client` | Claude LLM client responses | 174-187 |
| `mock_anthropic_client` | Anthropic API messages.create | 190-198 |
| `mock_knowledge_graph` | Neo4j graph operations | 201-215 |
| `mock_vector_db` | ChromaDB vector operations | 218-225 |
| `mock_concept_extractor` | ML concept extraction | 228-245 |
| `mock_cache` | In-memory cache | 248-270 |
| `mock_env_vars` | Environment variables | 299-312 |
| `mock_context_compressor` | Context compression | 452-463 |
| `mock_artifact_state_manager` | Artifact storage | 466-495 |
| `mock_skill_loader` | Skill loading | 498-510 |
| `mock_scholar_eval_validator` | ScholarEval validation | 513-535 |
| `mock_plan_creator` | Plan creation | 538-547 |
| `mock_plan_reviewer` | Plan review | 550-569 |
| `mock_delegation_manager` | Task delegation | 572-592 |
| `mock_novelty_detector` | Novelty detection | 595-617 |

### Migration Tasks

- [ ] **Task 1.1**: Create real LLM client test fixture
  - Requires: Valid `ANTHROPIC_API_KEY`
  - Implementation: Create fixture that uses real Claude API with rate limiting
  - Add `@pytest.mark.requires_claude` marker
  - Consider using cheaper model (haiku) for tests

- [ ] **Task 1.2**: Create real Neo4j test fixture
  - Requires: Neo4j instance (Docker or local)
  - Implementation: Use testcontainers-python for Neo4j
  - Add `@pytest.mark.requires_neo4j` marker
  - Create test-specific database that gets cleaned after tests

- [ ] **Task 1.3**: Create real ChromaDB test fixture
  - Requires: ChromaDB installation
  - Implementation: Use ephemeral ChromaDB client with in-memory storage
  - Add `@pytest.mark.requires_chromadb` marker

- [ ] **Task 1.4**: Create real cache test fixture
  - Requires: Redis (optional) or file-based cache
  - Implementation: Use temp directory for file-based cache in tests

---

## 2. Unit Tests with Mocks

### 2.1 Core Module Tests

#### `tests/unit/core/test_llm.py`

**Current Mocks**:
```python
@pytest.fixture
def mock_anthropic():
    with patch('kosmos.core.llm.Anthropic') as mock:
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response from Claude")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock
```

**What's Being Mocked**:
- Anthropic client initialization
- `messages.create()` API calls
- Token usage tracking

**Migration Tasks**:
- [ ] **Task 2.1.1**: Create real Claude API test
  - Replace mock with actual API call
  - Use `claude-3-haiku` for cost efficiency
  - Add retry logic for rate limits
  - Verify actual response structure matches expected

- [ ] **Task 2.1.2**: Test real token counting
  - Verify actual token counts from API
  - Compare with tiktoken estimates

- [ ] **Task 2.1.3**: Test real error handling
  - Test actual API error responses (rate limits, invalid keys)
  - Test network timeout handling

#### `tests/unit/core/test_async_llm.py`

**Current Mocks**: `AsyncMock` for async Claude operations

**Migration Tasks**:
- [ ] **Task 2.1.4**: Test real async API calls
  - Use actual `aiohttp` or `httpx` async client
  - Test concurrent request handling
  - Verify rate limiting behavior

---

### 2.2 Knowledge Module Tests

#### `tests/unit/knowledge/test_graph.py`

**Current Mocks**:
```python
@pytest.fixture
def knowledge_graph():
    with patch('py2neo.Graph'):
        with patch('kosmos.knowledge.graph.KnowledgeGraph._ensure_container_running'):
            kg = KnowledgeGraph(auto_start_container=False, create_indexes=False)
            kg.graph = Mock()
            kg.node_matcher = Mock()
            kg.rel_matcher = Mock()
            return kg
```

**What's Being Mocked**:
- `py2neo.Graph` connection
- Container startup
- Node/relationship matchers
- Cypher query execution

**Migration Tasks**:
- [ ] **Task 2.2.1**: Set up Neo4j testcontainer
  ```python
  from testcontainers.neo4j import Neo4jContainer

  @pytest.fixture(scope="module")
  def neo4j_container():
      with Neo4jContainer("neo4j:5.12") as neo4j:
          yield neo4j
  ```

- [ ] **Task 2.2.2**: Test real paper CRUD operations
  - Add real papers to graph
  - Query and verify data integrity
  - Test relationship creation

- [ ] **Task 2.2.3**: Test real Cypher queries
  - Execute actual graph traversals
  - Verify query performance
  - Test index usage

- [ ] **Task 2.2.4**: Test graph statistics
  - Verify node/relationship counts
  - Test aggregation queries

#### `tests/unit/knowledge/test_vector_db.py`

**Current Mocks**: ChromaDB client and collection operations

**Migration Tasks**:
- [ ] **Task 2.2.5**: Test real ChromaDB operations
  - Use ephemeral client: `chromadb.Client()`
  - Test actual embedding storage
  - Verify similarity search results

- [ ] **Task 2.2.6**: Test real embedding generation
  - Use actual SentenceTransformer model
  - Verify embedding dimensions
  - Test batch embedding performance

#### `tests/unit/knowledge/test_concept_extractor.py`

**Current Mocks**: LLM client for concept extraction

**Migration Tasks**:
- [ ] **Task 2.2.7**: Test real concept extraction
  - Use real Claude API
  - Verify extracted concepts are valid
  - Test different paper types

---

### 2.3 Literature Module Tests

#### `tests/unit/literature/test_arxiv_client.py`

**Current Mocks**:
```python
@pytest.fixture
def arxiv_client(mock_config):
    with patch('kosmos.literature.arxiv_client.get_config', return_value=mock_config):
        with patch('kosmos.literature.arxiv_client.get_cache') as mock_cache:
            mock_cache.return_value = None
            return ArxivClient(cache_enabled=False)
```

**What's Being Mocked**:
- Configuration loading
- Cache system
- arXiv API client
- Search results

**Migration Tasks**:
- [ ] **Task 2.3.1**: Test real arXiv API
  - Search for known papers (e.g., "Attention Is All You Need")
  - Verify metadata extraction
  - Test rate limiting compliance

- [ ] **Task 2.3.2**: Test real paper retrieval by ID
  - Fetch paper by arxiv_id "1706.03762"
  - Verify all metadata fields
  - Test PDF URL validity

- [ ] **Task 2.3.3**: Test real search pagination
  - Search with max_results > 100
  - Verify all results retrieved
  - Test result ordering

#### `tests/unit/literature/test_semantic_scholar.py`

**Current Mocks**: HTTP client and API responses

**Migration Tasks**:
- [ ] **Task 2.3.4**: Test real Semantic Scholar API
  - Requires: `SEMANTIC_SCHOLAR_API_KEY`
  - Test paper search
  - Test citation graph retrieval
  - Verify rate limit handling

#### `tests/unit/literature/test_pubmed_client.py`

**Current Mocks**: HTTP client and XML responses

**Migration Tasks**:
- [ ] **Task 2.3.5**: Test real PubMed API
  - Test ESearch and EFetch
  - Verify PMID retrieval
  - Test XML parsing with real responses

---

### 2.4 Agent Tests

#### `tests/unit/agents/test_research_director.py`

**Current Mocks**:
```python
@patch('kosmos.agents.research_director.get_client')
def test_generate_research_plan(self, mock_get_client, research_director):
    mock_client = Mock()
    mock_client.generate.return_value = "Research plan..."
    mock_get_client.return_value = mock_client
```

**What's Being Mocked**:
- Claude client for plan generation
- Agent message passing
- Workflow state transitions

**Migration Tasks**:
- [ ] **Task 2.4.1**: Test real research plan generation
  - Use real Claude API
  - Verify plan structure
  - Test different research domains

- [ ] **Task 2.4.2**: Test real agent communication
  - Set up actual agent instances
  - Verify message routing
  - Test async message handling

#### `tests/unit/agents/test_hypothesis_generator.py`

**Current Mocks**: LLM client for hypothesis generation

**Migration Tasks**:
- [ ] **Task 2.4.3**: Test real hypothesis generation
  - Generate hypotheses for known research questions
  - Verify hypothesis quality metrics
  - Test novelty scoring

#### `tests/unit/agents/test_data_analyst.py`

**Current Mocks**: LLM client for data interpretation

**Migration Tasks**:
- [ ] **Task 2.4.4**: Test real result interpretation
  - Provide real experiment results
  - Verify interpretation quality
  - Test statistical significance detection

---

### 2.5 Execution Module Tests

#### `tests/unit/execution/test_executor.py`

**Current Mocks**: Code execution results

**Migration Tasks**:
- [ ] **Task 2.5.1**: Test real code execution
  - Execute simple Python scripts
  - Verify output capture
  - Test error handling

#### `tests/unit/execution/test_docker_manager.py`

**Current Mocks**: Docker API client

**Migration Tasks**:
- [ ] **Task 2.5.2**: Test real Docker operations
  - Requires: Docker daemon
  - Test container lifecycle
  - Verify isolation

---

### 2.6 Hypothesis Module Tests

#### `tests/unit/hypothesis/test_novelty_checker.py`

**Current Mocks**: Literature search and vector DB

**Migration Tasks**:
- [ ] **Task 2.6.1**: Test real novelty checking
  - Search real literature databases
  - Compare with known novel/non-novel hypotheses
  - Verify scoring accuracy

#### `tests/unit/hypothesis/test_testability.py`

**Current Mocks**: LLM for testability assessment

**Migration Tasks**:
- [ ] **Task 2.6.2**: Test real testability analysis
  - Analyze known testable/untestable hypotheses
  - Verify scoring consistency
  - Test edge cases

---

## 3. Integration Tests with Mocks

### `tests/integration/test_analysis_pipeline.py`

**Current Mocks**:
```python
@patch('kosmos.agents.data_analyst.get_client')
@patch('kosmos.analysis.summarizer.get_client')
def test_full_pipeline_result_to_interpretation(self, ...):
    mock_client = Mock()
    mock_client.generate.return_value = '{"hypothesis_supported": true, ...}'
```

**What's Being Mocked**:
- DataAnalystAgent LLM client
- ResultSummarizer LLM client
- All Claude API calls

**Migration Tasks**:
- [ ] **Task 3.1.1**: Test real analysis pipeline
  - Execute full Result -> Interpretation flow
  - Use real Claude for interpretation
  - Verify output quality

- [ ] **Task 3.1.2**: Test real visualization generation
  - Generate actual matplotlib/plotly figures
  - Verify file output
  - Test different chart types

---

### `tests/integration/test_phase2_e2e.py`

**Current Mocks**:
```python
with patch('chromadb.Client'):
    with patch('py2neo.Graph'):
        with patch('sentence_transformers.SentenceTransformer'):
            with patch('kosmos.knowledge.graph.KnowledgeGraph._ensure_container_running'):
                # All external services mocked
```

**What's Being Mocked**:
- ChromaDB client
- Neo4j graph
- SentenceTransformer model
- Literature search
- LLM client

**Migration Tasks**:
- [ ] **Task 3.2.1**: Create Phase 2 real integration test
  - Set up all required services (Neo4j, ChromaDB)
  - Use real embedding model
  - Execute full literature pipeline

- [ ] **Task 3.2.2**: Test real knowledge graph construction
  - Build graph from real papers
  - Verify relationships
  - Test graph queries

---

### `tests/integration/test_phase3_e2e.py`

**Current Mocks**:
```python
@patch('kosmos.agents.hypothesis_generator.get_client')
@patch('kosmos.hypothesis.novelty_checker.UnifiedLiteratureSearch')
@patch('kosmos.hypothesis.novelty_checker.get_session')
def test_full_hypothesis_pipeline(...):
```

**What's Being Mocked**:
- Hypothesis generation LLM
- Literature search
- Database session

**Migration Tasks**:
- [ ] **Task 3.3.1**: Test real hypothesis pipeline
  - Generate real hypotheses with Claude
  - Check novelty against real literature
  - Analyze testability with real metrics

---

### `tests/integration/test_concurrent_research.py`

**Current Mocks**:
```python
@pytest.fixture
def mock_async_client(self):
    with patch('kosmos.agents.research_director.AsyncClaudeClient') as mock:
        client = AsyncMock()
        async def mock_batch_generate(requests):
            return [BatchResponse(...) for req in requests]
        client.batch_generate = mock_batch_generate
```

**What's Being Mocked**:
- AsyncClaudeClient batch operations
- ParallelExperimentExecutor
- All async LLM calls

**Migration Tasks**:
- [ ] **Task 3.4.1**: Test real concurrent operations
  - Use real async Claude client
  - Test actual parallelism
  - Verify rate limiting

- [ ] **Task 3.4.2**: Test real parallel experiment execution
  - Execute multiple experiments concurrently
  - Verify result aggregation
  - Test error handling in parallel context

---

### `tests/integration/test_orchestration_flow.py`

**Current Mocks**: AsyncMock for orchestration operations

**Migration Tasks**:
- [ ] **Task 3.5.1**: Test real orchestration flow
  - Run complete research cycle
  - Verify state transitions
  - Test convergence detection

---

### `tests/integration/test_cli.py`

**Current Mocks**: Configuration, cache manager, commands

**Migration Tasks**:
- [ ] **Task 3.6.1**: Test real CLI operations
  - Execute actual CLI commands
  - Verify file output
  - Test configuration loading

---

## 4. E2E Tests with Mocks

### `tests/e2e/test_autonomous_research.py`

**Current Mocks**: LLM client, research components

**Migration Tasks**:
- [ ] **Task 4.1.1**: Create full autonomous research E2E test
  - Requires all services running
  - Execute complete research workflow
  - Time limit: 30+ minutes expected
  - Add `@pytest.mark.slow` marker

---

## 5. Requirements Tests with Mocks

### Core Requirements (`tests/requirements/core/`)

#### `test_req_llm.py`
- [ ] **Task 5.1.1**: Test real LLM requirements with actual API

#### `test_req_configuration.py`
- [ ] **Task 5.1.2**: Test with real environment variables

### Data Analysis Requirements (`tests/requirements/data_analysis/`)

#### `test_req_daa_*.py` (5 files)
- [ ] **Task 5.2.1**: Test real data analysis agent capabilities
- [ ] **Task 5.2.2**: Test real code generation and execution
- [ ] **Task 5.2.3**: Test real summarization with Claude

### Orchestrator Requirements (`tests/requirements/orchestrator/`)

#### `test_req_orch_*.py` (6 files)
- [ ] **Task 5.3.1**: Test real orchestration lifecycle
- [ ] **Task 5.3.2**: Test real task management
- [ ] **Task 5.3.3**: Test real error handling

### World Model Requirements (`tests/requirements/world_model/`)

#### `test_req_wm_*.py` (5 files)
- [ ] **Task 5.4.1**: Test real world model persistence with Neo4j
- [ ] **Task 5.4.2**: Test real concurrency with multiple connections
- [ ] **Task 5.4.3**: Test real CRUD operations

### Scientific Requirements (`tests/requirements/scientific/`)

#### `test_req_sci_*.py` (6 files)
- [ ] **Task 5.5.1**: Test real hypothesis validation
- [ ] **Task 5.5.2**: Test real metric calculation
- [ ] **Task 5.5.3**: Test real reproducibility checks

---

## 6. Migration Strategy

### Phase 1: Infrastructure Setup (Week 1-2)

1. **Set up test containers**
   ```python
   # pyproject.toml or requirements-test.txt
   testcontainers[neo4j]>=3.7.0
   testcontainers[redis]>=3.7.0
   ```

2. **Create base fixtures for real services**
   ```python
   # tests/fixtures/real_services.py
   import pytest
   from testcontainers.neo4j import Neo4jContainer

   @pytest.fixture(scope="session")
   def real_neo4j():
       with Neo4jContainer("neo4j:5.12") as neo4j:
           yield {
               "uri": neo4j.get_connection_url(),
               "user": "neo4j",
               "password": neo4j.NEO4J_ADMIN_PASSWORD
           }
   ```

3. **Create API key management**
   ```python
   @pytest.fixture
   def real_claude_client():
       api_key = os.getenv("ANTHROPIC_API_KEY")
       if not api_key or api_key.startswith("test"):
           pytest.skip("Real API key required")
       return ClaudeClient(model="claude-3-haiku-20240307")  # Use cheapest model
   ```

### Phase 2: Core Tests Migration (Week 3-4)

1. Convert `test_llm.py` to use real API
2. Convert `test_graph.py` to use real Neo4j
3. Convert `test_vector_db.py` to use real ChromaDB

### Phase 3: Agent Tests Migration (Week 5-6)

1. Convert agent tests to use real LLM
2. Add rate limiting and retry logic
3. Create test data fixtures

### Phase 4: Integration Tests Migration (Week 7-8)

1. Convert pipeline tests
2. Convert E2E tests
3. Performance benchmarking

### Phase 5: Requirements Tests Migration (Week 9-10)

1. Convert all requirements tests
2. Verify all requirements pass with real services
3. Update documentation

---

## 7. Implementation Checklist

### Pre-Migration Checklist

- [ ] Install testcontainers: `pip install testcontainers[neo4j,redis]`
- [ ] Set up test environment variables in `.env.test`
- [ ] Create CI/CD secrets for API keys
- [ ] Set up Docker for local testing
- [ ] Create cost budget for Claude API testing

### Test Markers to Add

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "real_api: requires real external API")
    config.addinivalue_line("markers", "real_db: requires real database")
    config.addinivalue_line("markers", "expensive: uses paid API calls")
    config.addinivalue_line("markers", "slow: takes more than 10 seconds")
```

### Running Real Tests

```bash
# Run only mock tests (fast, no API costs)
pytest -m "not real_api and not real_db"

# Run real API tests (requires keys, incurs costs)
pytest -m "real_api" --run-expensive

# Run real database tests (requires Docker)
pytest -m "real_db"

# Run all real tests
pytest -m "real_api or real_db" --run-expensive
```

### CI/CD Configuration

```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run mock tests
        run: pytest -m "not real_api and not real_db"

  integration-tests:
    runs-on: ubuntu-latest
    services:
      neo4j:
        image: neo4j:5.12
    steps:
      - name: Run real DB tests
        run: pytest -m "real_db"

  api-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'  # Only on scheduled runs to save costs
    steps:
      - name: Run real API tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: pytest -m "real_api" --run-expensive
```

---

## Detailed Task List by File

### High Priority (Core Functionality)

| File | Mock Type | Task ID | Estimated Effort |
|------|-----------|---------|------------------|
| `tests/unit/core/test_llm.py` | Claude API | 2.1.1-2.1.3 | 4 hours |
| `tests/unit/knowledge/test_graph.py` | Neo4j | 2.2.1-2.2.4 | 6 hours |
| `tests/unit/knowledge/test_vector_db.py` | ChromaDB | 2.2.5-2.2.6 | 4 hours |
| `tests/unit/agents/test_research_director.py` | Claude API | 2.4.1-2.4.2 | 6 hours |
| `tests/integration/test_analysis_pipeline.py` | Multiple | 3.1.1-3.1.2 | 8 hours |

### Medium Priority (Extended Functionality)

| File | Mock Type | Task ID | Estimated Effort |
|------|-----------|---------|------------------|
| `tests/unit/literature/test_arxiv_client.py` | arXiv API | 2.3.1-2.3.3 | 3 hours |
| `tests/unit/literature/test_semantic_scholar.py` | S2 API | 2.3.4 | 2 hours |
| `tests/integration/test_phase2_e2e.py` | Multiple | 3.2.1-3.2.2 | 8 hours |
| `tests/integration/test_phase3_e2e.py` | Multiple | 3.3.1 | 6 hours |

### Lower Priority (Requirements Validation)

| File | Mock Type | Task ID | Estimated Effort |
|------|-----------|---------|------------------|
| `tests/requirements/core/*.py` | Various | 5.1.x | 4 hours |
| `tests/requirements/data_analysis/*.py` | Various | 5.2.x | 6 hours |
| `tests/requirements/orchestrator/*.py` | Various | 5.3.x | 6 hours |
| `tests/requirements/world_model/*.py` | Neo4j | 5.4.x | 4 hours |
| `tests/requirements/scientific/*.py` | Various | 5.5.x | 4 hours |

---

## Appendix: Current Mock Patterns Reference

### Pattern 1: Direct Patching
```python
@patch('module.path.to.Class')
def test_something(self, mock_class):
    mock_class.return_value.method.return_value = "value"
```

### Pattern 2: Context Manager Patching
```python
with patch('module.path') as mock:
    mock.return_value = Mock()
    # test code
```

### Pattern 3: Fixture-based Mocking
```python
@pytest.fixture
def mock_client():
    mock = Mock()
    mock.method.return_value = "value"
    return mock
```

### Pattern 4: AsyncMock for Async Code
```python
from unittest.mock import AsyncMock

async_mock = AsyncMock()
async_mock.async_method.return_value = "result"
```

### Pattern 5: Nested Patches
```python
with patch('module1.Class1'):
    with patch('module2.Class2'):
        with patch('module3.Class3'):
            # deeply nested mocking
```

---

## Cost Estimation for Real API Tests

| Test Category | Est. API Calls | Model | Est. Cost/Run |
|--------------|----------------|-------|---------------|
| Core LLM Tests | 20 | haiku | $0.05 |
| Agent Tests | 50 | haiku | $0.12 |
| Integration Tests | 100 | haiku | $0.25 |
| E2E Tests | 200 | sonnet | $1.50 |
| **Total** | **370** | mixed | **~$2.00** |

*Estimates based on Claude 3 Haiku: $0.25/1M input, $1.25/1M output*
*Claude 3.5 Sonnet: $3/1M input, $15/1M output*

---

## Success Criteria

1. **Coverage**: All previously mocked functionality has real-world test coverage
2. **Reliability**: Real tests pass consistently (>95% pass rate)
3. **Performance**: Real tests complete within CI timeout limits
4. **Cost**: Monthly API test costs stay under $100
5. **Maintainability**: Test infrastructure is documented and easy to update
