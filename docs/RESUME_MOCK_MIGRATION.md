# Resume Mock to Real Test Migration

## Context
We are converting mock-based tests to use real LLM API calls to ensure production readiness.

## Completed
- **Phase 1: Core LLM tests** - All 43 tests pass with real APIs
  - `tests/unit/core/test_llm.py` (17 tests)
  - `tests/unit/core/test_async_llm.py` (13 tests)
  - `tests/unit/core/test_litellm_provider.py` (13 tests)

## Resume Task
Continue with **Phase 2: Knowledge Layer Tests**

### Files to Convert
1. `tests/unit/knowledge/test_embeddings.py` - Uses SentenceTransformer mock
2. `tests/unit/knowledge/test_concept_extractor.py` - Uses Claude API mock
3. `tests/unit/knowledge/test_vector_db.py` - Uses ChromaDB mock
4. `tests/unit/knowledge/test_graph.py` - Uses Neo4j mock

### Pattern to Follow
```python
import os
import pytest
import uuid

pytestmark = [
    pytest.mark.requires_claude,
    pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="Requires ANTHROPIC_API_KEY"
    )
]

def unique_prompt(base: str) -> str:
    """Add unique suffix to avoid cache hits."""
    return f"{base} [test-id: {uuid.uuid4().hex[:8]}]"
```

### Fixtures Available (in conftest.py)
- `real_anthropic_client` - Anthropic client
- `deepseek_client` - DeepSeek via LiteLLM
- `real_vector_db` - Ephemeral ChromaDB
- `real_embedder` - SentenceTransformer (all-MiniLM-L6-v2)
- `real_knowledge_graph` - Neo4j connection

### API Keys Required
- ANTHROPIC_API_KEY - Set
- DEEPSEEK_API_KEY - Set
- SEMANTIC_SCHOLAR_API_KEY - Pending (may be needed for literature tests)

### Verification Command
```bash
set -a && source .env && set +a && pytest tests/unit/knowledge/ -v --no-cov
```

## Full Plan
See: `docs/CHECKPOINT_MOCK_MIGRATION.md` and `/home/jim/.claude/plans/sprightly-finding-puddle.md`
