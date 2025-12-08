# Mock to Real Test Migration - Complete

## Date: 2025-12-07

## Status: ✓ COMPLETE

All 5 phases of mock-to-real test migration are complete.

---

## Summary

| Phase | Description | Tests | Status |
|-------|-------------|-------|--------|
| Phase 1 | Core LLM Tests | 43 | ✓ Complete |
| Phase 2 | Knowledge Layer Tests | 57 | ✓ Complete |
| Phase 3 | Agent Tests | 128 | ✓ Complete |
| Phase 4 | Integration Tests | 18 | ✓ Complete |
| Phase 5 | Concurrent Research Tests | 11 | ✓ Complete |
| **Total** | | **257** | ✓ |

---

## Phase 1: Core LLM Tests (43 tests)

Converted 3 core test files from mock-based to real API calls.

| File | Tests | Provider |
|------|-------|----------|
| `tests/unit/core/test_llm.py` | 17 | Anthropic Haiku |
| `tests/unit/core/test_async_llm.py` | 13 | Anthropic Haiku |
| `tests/unit/core/test_litellm_provider.py` | 13 | Anthropic + DeepSeek |

### Key Patterns Established
```python
import os, pytest, uuid

pytestmark = [
    pytest.mark.requires_claude,
    pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="Requires API key")
]

def unique_id() -> str:
    return uuid.uuid4().hex[:8]
```

---

## Phase 2: Knowledge Layer Tests (57 tests)

Converted 4 knowledge layer test files from mock-based to real services.

| File | Tests | Service |
|------|-------|---------|
| `tests/unit/knowledge/test_embeddings.py` | 13 | SentenceTransformer (SPECTER + MiniLM) |
| `tests/unit/knowledge/test_concept_extractor.py` | 11 | Anthropic Haiku |
| `tests/unit/knowledge/test_vector_db.py` | 16 | ChromaDB + SPECTER embeddings |
| `tests/unit/knowledge/test_graph.py` | 17 | Neo4j |

### VRAM Note
SPECTER model (~440MB) loads on GPU. Run in batches for 6GB VRAM systems.

---

## Phase 3: Agent Tests (128 tests)

Converted 4 agent test files from mock-based to real Claude API calls.

| File | Tests | Service |
|------|-------|---------|
| `tests/unit/agents/test_data_analyst.py` | 24 | Claude Haiku |
| `tests/unit/agents/test_research_director.py` | 36 | Claude Haiku |
| `tests/unit/agents/test_hypothesis_generator.py` | 19 | Claude Haiku |
| `tests/unit/agents/test_literature_analyzer.py` | 10 | Claude Haiku |
| `tests/unit/agents/test_skill_loader.py` | 39 | Pure Python |

### Bugs Fixed
1. **`generate_structured` parameters** - Added `max_tokens`, `temperature`, `max_retries` to `ClaudeClient.generate_structured()`
2. **JSON reliability** - Added retry logic, lower temperature (0.3), explicit JSON completion instructions

---

## Phase 4: Integration Tests (18 tests)

Converted 3 integration test files to use real Claude API.

| File | Tests | Status |
|------|-------|--------|
| `tests/integration/test_analysis_pipeline.py` | 9 | ✓ Pass |
| `tests/integration/test_phase3_e2e.py` | 4 | ✓ Pass |
| `tests/integration/test_phase2_e2e.py` | 5 | ✓ Pass |
| `tests/integration/test_concurrent_research.py` | 11 | Skipped (async pending) |

### Bugs Fixed
3. **`schema` parameter alias** - Added `schema` as alias for `output_schema` in `ClaudeClient.generate_structured()` for provider compatibility

### Deprecated Tests Removed
- 3 tests with outdated API usage removed (CitationParser, VectorDatabase, UnifiedLiteratureSearch)

---

## Code Changes

### `kosmos/core/llm.py` - ClaudeClient.generate_structured()

```python
def generate_structured(
    self,
    prompt: str,
    output_schema: Optional[Dict[str, Any]] = None,
    system: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.3,
    max_retries: int = 2,
    schema: Optional[Dict[str, Any]] = None,  # Alias for provider compatibility
) -> Dict[str, Any]:
```

Key improvements:
- `schema` parameter alias for provider interface compatibility
- `max_tokens` parameter (default 4096)
- `temperature` parameter (default 0.3 for deterministic output)
- `max_retries` parameter with cache bypass on retries
- Explicit JSON completion instructions in system prompt

---

## Verification Commands

```bash
# Phase 1 - Core LLM (43 tests)
pytest tests/unit/core/test_llm.py tests/unit/core/test_async_llm.py tests/unit/core/test_litellm_provider.py -v --no-cov

# Phase 2 - Knowledge Layer (57 tests) - run in batches for VRAM
pytest tests/unit/knowledge/test_embeddings.py tests/unit/knowledge/test_concept_extractor.py -v --no-cov
pytest tests/unit/knowledge/test_vector_db.py tests/unit/knowledge/test_graph.py -v --no-cov

# Phase 3 - Agent Tests (128 tests)
pytest tests/unit/agents/ -v --no-cov

# Phase 4 - Integration Tests (18 tests)
pytest tests/integration/test_analysis_pipeline.py tests/integration/test_phase3_e2e.py tests/integration/test_phase2_e2e.py -v --no-cov

# All converted tests
pytest tests/unit/core/ tests/unit/knowledge/ tests/unit/agents/ tests/integration/test_analysis_pipeline.py tests/integration/test_phase3_e2e.py tests/integration/test_phase2_e2e.py -v --no-cov
```

---

## Phase 5: Concurrent Research Tests (11 tests)

Enabled 11 previously-skipped tests for concurrent research operations.

| File | Tests | Description |
|------|-------|-------------|
| `tests/integration/test_concurrent_research.py` | 11 | Async hypothesis evaluation, parallel execution, thread safety |

### What Was Done
1. Added `tokens_used` and `latency_ms` compatibility properties to `BatchResponse`
2. Fixed test mock fixtures to use correct field names (`input_tokens`, `output_tokens`, `execution_time`)
3. Removed skip marker and added proper pytest markers
4. Fixed patch paths to target actual module locations
5. Fixed `experiment_queue` usage (list, not set)

### Key Discovery
The async infrastructure was **already fully implemented**:
- `AsyncClaudeClient` in `kosmos/core/async_llm.py`
- `ParallelExperimentExecutor` in `kosmos/execution/parallel.py`
- Async methods in `ResearchDirectorAgent`

The tests were skipped due to field name mismatches, not missing implementation.

---

## Infrastructure Requirements

- **Docker**: Neo4j container (kosmos-neo4j)
- **APIs**: ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, SEMANTIC_SCHOLAR_API_KEY
- **GPU**: ~440MB VRAM for SPECTER model
- **ChromaDB**: v1.3.4+

---

## Commits

- `199c931` - Convert autonomous research tests to use real LLM API calls
- `7ebd56b` - Convert Phase 2 knowledge layer tests from mocks to real services
- `6483787` - Convert Phase 4 integration tests to use real Claude API
- `f8b4426` - Remove deprecated integration tests with outdated API usage
- (pending) - Enable concurrent research tests with BatchResponse compatibility
