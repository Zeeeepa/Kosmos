# E2E Testing Dependency Report

**Generated:** 2025-11-26 (Updated)
**Project:** Kosmos AI Scientist
**Purpose:** Identify all blockers preventing E2E testing production readiness

---

## Executive Summary

### Current Test Status
| Category | Count | Status |
|----------|-------|--------|
| Total Tests Collected | 2,118 | Available |
| Collection Errors | 43 files | **Blocking** |
| Unit Tests Skipped (API mismatch) | 7 files (~35 tests) | **Blocking** |
| Unit Tests Passing | ~250+ | Working |
| E2E Tests | 23 | Require API keys |

### Environment Status (Actual)
| Resource | Status | Notes |
|----------|--------|-------|
| Python | 3.11.11 | OK |
| API Keys | **Configured** | DeepSeek via OpenAI-compatible API |
| Docker | **Running** | v29.0.1 |
| Redis | Disabled | `ENABLE_REDIS_CACHE=false` |
| Neo4j | Not configured | Would enable knowledge graph tests |
| SQLite | Configured | `sqlite:///./kosmos.db` |

### Top Blockers (Priority Order)
| # | Blocker | Tests Blocked | Fix Effort |
|---|---------|---------------|------------|
| 1 | Missing pytest markers (`requirement`, `category`, `priority`) | 43 files (~500+ tests) | **2 minutes** |
| 2 | 7 unit test files skipped (API mismatch) | ~35 tests | 4-8 hours |
| 3 | Runtime errors in unit tests | Unknown | 2-4 hours |

---

## Section 1: Collection Errors (CRITICAL)

### 1.1 Root Cause Identified

**Issue:** `pytest.ini` has `--strict-markers` enabled, but 3 markers are not defined:

```
'requirement' not found in `markers` configuration option
```

**Affected Files:** All files in `tests/requirements/` (43 files)

**Markers Missing:**
- `requirement` - Used as `@pytest.mark.requirement("REQ-DAA-EXEC-001")`
- `category` - Used as `@pytest.mark.category("data_analysis")`
- `priority` - Used as `@pytest.mark.priority("MUST")`

### 1.2 Fix Required

Add to `pytest.ini` markers section:
```ini
    requirement: Requirement ID marker for traceability
    category: Test category (data_analysis, scientific, etc.)
    priority: Priority level (MUST, SHOULD, MAY)
```

**Estimated Fix Time:** 2 minutes
**Tests Unlocked:** ~500+ tests in 43 files

### 1.3 Affected Directories
```
tests/requirements/
├── data_analysis/ (8 files)
├── performance/ (5 files)
├── scientific/ (4 files)
├── security/ (3 files)
├── validation/ (6 files)
└── world_model/ (5 files)
```

---

## Section 2: Skipped Unit Test Files (HIGH PRIORITY)

### 2.1 Files with Module-Level Skip

All 7 files have identical skip pattern at line 2:
```python
pytest.skip('Test needs API update to match current implementation', allow_module_level=True)
```

| Test File | Component | Est. Tests | Fix Effort |
|-----------|-----------|------------|------------|
| `tests/unit/knowledge/test_vector_db.py` | VectorDatabase | 5+ | 4 hours |
| `tests/unit/knowledge/test_embeddings.py` | EmbeddingGenerator | 5+ | 4 hours |
| `tests/unit/hypothesis/test_refiner.py` | HypothesisRefiner | 5+ | 4 hours |
| `tests/unit/literature/test_arxiv_client.py` | ArxivClient | 5+ | 4 hours |
| `tests/unit/literature/test_pubmed_client.py` | PubMedClient | 5+ | 4 hours |
| `tests/unit/literature/test_semantic_scholar.py` | SemanticScholarClient | 5+ | 4 hours |
| `tests/unit/core/test_profiling.py` | Profiling API | 3+ | 2 hours |

**Total:** ~35+ tests skipped
**Total Fix Time:** 4-8 hours (some can be parallelized)

### 2.2 Fix Strategy Per File

For each file:
1. Remove `pytest.skip()` at module level (line 2)
2. Run tests: `pytest <file> -v --tb=short`
3. Identify actual API mismatches from failures
4. Update test expectations to match current implementation
5. Verify all tests pass

---

## Section 3: Environment Configuration

### 3.1 Current .env Configuration (Detected)

```bash
# LLM Provider (DeepSeek via OpenAI-compatible)
OPENAI_API_KEY=sk-REDACTED-key-revoked
OPENAI_MODEL=deepseek-chat
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7

# Anthropic (dummy key - not functional)
ANTHROPIC_API_KEY=sk-ant-dummy...

# Database
DATABASE_URL=sqlite:///./kosmos.db

# Cache
ENABLE_REDIS_CACHE=false
```

### 3.2 Services Running
- **Docker:** Running (v29.0.1)
- **Redis:** Disabled in config
- **Neo4j:** Not configured
- **ChromaDB:** Not configured

### 3.3 What This Means for E2E Tests

| E2E Test Type | Can Run? | Notes |
|---------------|----------|-------|
| Mock mode tests | Yes | Always available |
| LLM integration | Yes | Via DeepSeek |
| Docker/sandbox | Yes | Docker available |
| Knowledge graph | No | Neo4j not configured |
| Cache tests | No | Redis disabled |

---

## Section 4: Service Requirements Matrix

| Test Category | LLM | Docker | Neo4j | Redis | ChromaDB |
|---------------|-----|--------|-------|-------|----------|
| unit (gap modules) | Mock | No | No | No | No |
| unit (literature) | Mock | No | No | No | No |
| unit (knowledge) | Mock | No | Optional | No | Optional |
| unit (execution) | No | Yes | No | No | No |
| integration | Mock/Real | No | Mock | Mock | Mock |
| e2e | Real | Yes | Optional | Optional | Optional |
| requirements | Mock/Real | Varies | Varies | Varies | Varies |

---

## Section 5: Dependency Resolution Strategy

### Tier 0: Immediate (< 5 minutes)

| Fix ID | Task | Command | Tests Unlocked |
|--------|------|---------|----------------|
| T0-001 | Add missing pytest markers | Edit `pytest.ini` | 500+ (43 files) |

### Tier 1: Quick Wins (< 1 hour)

| Fix ID | Task | Effort | Tests Unlocked |
|--------|------|--------|----------------|
| T1-001 | Configure Neo4j | 15 min | 5+ knowledge tests |
| T1-002 | Enable Redis | 5 min | 3+ cache tests |
| T1-003 | Build sandbox image | 15 min | 6+ execution tests |

### Tier 2: Medium Effort (4-8 hours)

| Fix ID | Task | Effort | Tests Unlocked |
|--------|------|--------|----------------|
| T2-001 | Fix test_vector_db.py | 4 hr | 5+ tests |
| T2-002 | Fix test_embeddings.py | 4 hr | 5+ tests |
| T2-003 | Fix test_refiner.py | 4 hr | 5+ tests |
| T2-004 | Fix test_arxiv_client.py | 4 hr | 5+ tests |
| T2-005 | Fix test_pubmed_client.py | 4 hr | 5+ tests |
| T2-006 | Fix test_semantic_scholar.py | 4 hr | 5+ tests |
| T2-007 | Fix test_profiling.py | 2 hr | 3+ tests |

---

## Section 6: Critical Path to Production

```
T0-001 (2 min)
    │
    ▼
┌───────────────────────────────────────┐
│     43 requirement test files         │
│     now collectible (~500+ tests)     │
└───────────────────────────────────────┘
    │
    ├─────────────────┬─────────────────┐
    ▼                 ▼                 ▼
T2-001-007        T1-001-003       Run E2E
(4-8 hr)          (35 min)         with DeepSeek
    │                 │                 │
    ▼                 ▼                 ▼
Unit tests        Services          E2E tests
restored          available         validated
    │                 │                 │
    └─────────────────┴─────────────────┘
                      │
                      ▼
              PRODUCTION READY
              (2,000+ tests passing)
```

---

## Section 7: Test Environment Profiles

### Profile: Minimal (Current State)
```bash
# Works with current config
pytest tests/unit -m "not requires_api_key and not requires_neo4j"
# Expected: ~250 tests (after marker fix: ~750+)
```

### Profile: Full Local
```bash
# Requires: marker fix + Neo4j + Redis
pytest tests/
# Expected: 2,000+ tests (after all fixes)
```

---

## Validation Checklist

- [x] Collection errors root cause identified (missing markers)
- [x] All skipped test files documented (7 files)
- [x] Environment status verified (API keys present, Docker running)
- [x] Service requirements mapped
- [x] Fix effort estimates provided
- [ ] Marker fix applied
- [ ] Skipped tests restored
- [ ] Full test suite passing

---

## Next Steps

1. **Immediate:** Add missing markers to `pytest.ini` (T0-001)
2. **Parallel A:** Fix 7 skipped unit test files (T2-001 to T2-007)
3. **Parallel B:** Configure optional services (Neo4j, Redis)
4. **Validate:** Run full E2E suite with DeepSeek

---

*Report regenerated to reflect actual codebase state as of 2025-11-26*
*Previous report was outdated (described ~300 tests, actual: 2,118)*
