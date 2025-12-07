# Mock to Real Test Migration - Checkpoint

## Date: 2025-12-07

## Phase 1 Complete: Core LLM Tests

### Summary
Converted 3 core test files from mock-based to real API calls. All 43 tests pass.

### Files Converted

| File | Tests | Provider |
|------|-------|----------|
| `tests/unit/core/test_llm.py` | 17 | Anthropic Haiku |
| `tests/unit/core/test_async_llm.py` | 13 | Anthropic Haiku |
| `tests/unit/core/test_litellm_provider.py` | 13 | Anthropic + DeepSeek |

### Key Changes

1. **`tests/conftest.py`** - Added real service fixtures:
   - `deepseek_client` - LiteLLM client for DeepSeek
   - `real_anthropic_client` - Real Anthropic client
   - `real_vector_db` - Ephemeral ChromaDB
   - `real_embedder` - SentenceTransformer
   - `real_knowledge_graph` - Neo4j connection

2. **Pattern established**: Use `unique_prompt()` helper to avoid cache hits:
   ```python
   def unique_prompt(base: str) -> str:
       return f"{base} [test-id: {uuid.uuid4().hex[:8]}]"
   ```

3. **Markers used**: `@pytest.mark.requires_claude` for tests needing Anthropic API

### Infrastructure Status
- Docker: Running
- Neo4j: Running (kosmos-neo4j)
- ChromaDB: v1.3.4
- ANTHROPIC_API_KEY: Configured
- DEEPSEEK_API_KEY: Configured
- SEMANTIC_SCHOLAR_API_KEY: Pending (waiting for approval)

### Run Tests
```bash
# Phase 1 tests only
pytest tests/unit/core/test_llm.py tests/unit/core/test_async_llm.py tests/unit/core/test_litellm_provider.py -v --no-cov

# Full E2E (already uses real APIs)
make test-e2e
```

## Remaining Phases

### Phase 2: Knowledge Layer (4 files)
- `tests/unit/knowledge/test_embeddings.py`
- `tests/unit/knowledge/test_concept_extractor.py`
- `tests/unit/knowledge/test_vector_db.py`
- `tests/unit/knowledge/test_graph.py`

### Phase 3: Agents (4 files)
- `tests/unit/agents/test_research_director.py`
- `tests/unit/agents/test_hypothesis_generator.py`
- `tests/unit/agents/test_literature_analyzer.py`
- `tests/unit/agents/test_data_analyst.py`

### Phase 4: Integration (4 files)
- `tests/integration/test_analysis_pipeline.py`
- `tests/integration/test_phase2_e2e.py`
- `tests/integration/test_phase3_e2e.py`
- `tests/integration/test_concurrent_research.py`

## Plan File
Full migration plan: `/home/jim/.claude/plans/sprightly-finding-puddle.md`
