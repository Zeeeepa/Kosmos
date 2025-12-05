# Kosmos E2E Testing Implementation Plan

**Generated:** 2025-11-26 (Updated)
**Based on:** E2E_TESTING_DEPENDENCY_REPORT.md (Updated)
**Current Test Count:** 2,118 tests (43 files blocked by collection errors)
**LLM Provider:** DeepSeek via OpenAI-compatible API

---

## Executive Summary

### Actual Current State
- **2,118 tests** collected (not ~300 as previously documented)
- **43 files** fail collection due to missing pytest markers
- **7 files** skipped at module level (API mismatch)
- **API keys configured** - DeepSeek via OpenAI-compatible API
- **Docker running** - v29.0.1

### What's Achievable NOW
After a 2-minute marker fix:
- ~500+ additional tests become collectible
- E2E tests can run with DeepSeek API
- Docker-based execution tests available

### Critical Fixes Required
1. **T0-001:** Add missing pytest markers (2 min) → unlocks 500+ tests
2. **T2-001-007:** Fix 7 skipped unit test files (4-8 hr) → unlocks 35+ tests
3. **Runtime fixes:** Address test failures as discovered

---

## Phase 1: Immediate Fixes (Day 1)

### 1.1 Add Missing Pytest Markers (T0-001)

**File:** `pytest.ini`
**Time:** 2 minutes

```ini
# Add to markers section:
    requirement: Requirement ID marker for traceability
    category: Test category (data_analysis, scientific, etc.)
    priority: Priority level (MUST, SHOULD, MAY)
```

**Verification:**
```bash
pytest tests/requirements --collect-only -q
# Expected: 500+ tests collected (was 0)
```

### 1.2 Run Baseline Test Suite

After marker fix:
```bash
# Check collection success
pytest tests/ --collect-only -q 2>&1 | tail -5

# Run unit tests
pytest tests/unit -v --tb=short -x

# Check pass rate
pytest tests/unit --tb=no -q
```

---

## Phase 2: Restore Skipped Unit Tests (Days 1-2)

### 2.1 Files to Restore

| Priority | File | Component | Strategy |
|----------|------|-----------|----------|
| 1 | `test_vector_db.py` | VectorDatabase | Critical for search |
| 2 | `test_embeddings.py` | EmbeddingGenerator | Required by vector DB |
| 3 | `test_refiner.py` | HypothesisRefiner | Core logic |
| 4 | `test_arxiv_client.py` | ArxivClient | Literature retrieval |
| 5 | `test_pubmed_client.py` | PubMedClient | Literature retrieval |
| 6 | `test_semantic_scholar.py` | SemanticScholarClient | Literature retrieval |
| 7 | `test_profiling.py` | ProfileResult | Performance monitoring |

### 2.2 Restoration Process Per File

```bash
# For each file:

# 1. Remove skip
# Edit file, remove line 2: pytest.skip('Test needs API update...', allow_module_level=True)

# 2. Run and capture failures
pytest tests/unit/knowledge/test_vector_db.py -v --tb=long 2>&1 | tee /tmp/vector_db_failures.log

# 3. Analyze failures
grep -E "FAILED|ERROR|AssertionError" /tmp/vector_db_failures.log

# 4. Fix each failure (update test expectations or mocks)

# 5. Verify all pass
pytest tests/unit/knowledge/test_vector_db.py -v
```

### 2.3 Common Fix Patterns

Based on typical API drift:

**Pattern A: Constructor signature changed**
```python
# Old: SomeClass(arg1, arg2)
# New: SomeClass(config=Config(arg1, arg2))

# Fix: Update test instantiation
```

**Pattern B: Method renamed or signature changed**
```python
# Old: obj.do_thing(a, b)
# New: obj.execute(a, b, timeout=30)

# Fix: Update method calls in tests
```

**Pattern C: Return type changed**
```python
# Old: Returns dict
# New: Returns dataclass

# Fix: Update assertions to match new type
```

---

## Phase 3: E2E Test Validation (Day 2-3)

### 3.1 Run E2E Tests with DeepSeek

```bash
# Set environment (already configured)
export OPENAI_API_KEY=sk-REDACTED-key-revoked
export OPENAI_BASE_URL=https://api.deepseek.com
export OPENAI_MODEL=deepseek-chat

# Run E2E tests
pytest tests/e2e -v --tb=short --timeout=300
```

### 3.2 Expected E2E Test Results

| Test File | Tests | Expected Status |
|-----------|-------|-----------------|
| `test_system_sanity.py` | ~10 | Pass with LLM |
| `test_autonomous_research.py` | ~5 | Pass (mock mode) |
| `test_full_research_workflow.py` | ~8 | Pass with DeepSeek |

### 3.3 E2E Tests That May Skip

These tests require services not currently configured:
- Knowledge graph tests (Neo4j)
- Redis cache tests (disabled)

---

## Phase 4: Full Test Suite (Day 3+)

### 4.1 Run Complete Suite

```bash
# Full run with coverage
pytest tests/ -v --cov=kosmos --cov-report=term-missing --tb=short

# Generate HTML report
pytest tests/ --cov=kosmos --cov-report=html:htmlcov
```

### 4.2 Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| Tests collected | 2,118+ | 2,118 (43 errors) |
| Collection errors | 0 | 43 |
| Unit tests passing | >95% | Unknown |
| E2E tests passing | >80% | Unknown |
| Coverage | >70% | Unknown |

---

## Gap Module Test Coverage

### Current Status by Gap

| Gap | Module | Has Tests | Status |
|-----|--------|-----------|--------|
| 0 | Context Compression | Yes | Likely working |
| 1 | State Management | Yes | Likely working |
| 2 | Task Generation | Yes | Likely working |
| 3 | Agent Integration | Partial | Some skipped |
| 4 | Execution Environment | Yes | Requires Docker |
| 5 | Discovery Validation | Yes | Likely working |

### Tests Per Gap After Restoration

| Gap | Test Files | Est. Tests |
|-----|------------|------------|
| Gap 0 | compression/*.py | 10+ |
| Gap 1 | world_model/*.py | 15+ |
| Gap 2 | orchestration/*.py | 20+ |
| Gap 3 | agents/*.py | 25+ |
| Gap 4 | execution/*.py | 15+ |
| Gap 5 | validation/*.py | 10+ |

---

## Fix → Test Unlock Map (Appendix A)

| Fix ID | Fix Description | Effort | Tests Unlocked | Depends On |
|--------|-----------------|--------|----------------|------------|
| T0-001 | Add pytest markers (requirement, category, priority) | 2 min | 500+ | None |
| T2-001 | Restore test_vector_db.py | 4 hr | 5+ | None |
| T2-002 | Restore test_embeddings.py | 4 hr | 5+ | None |
| T2-003 | Restore test_refiner.py | 4 hr | 5+ | None |
| T2-004 | Restore test_arxiv_client.py | 4 hr | 5+ | None |
| T2-005 | Restore test_pubmed_client.py | 4 hr | 5+ | None |
| T2-006 | Restore test_semantic_scholar.py | 4 hr | 5+ | None |
| T2-007 | Restore test_profiling.py | 2 hr | 3+ | None |
| T1-001 | Configure Neo4j | 15 min | 5+ | Docker |
| T1-002 | Enable Redis | 5 min | 3+ | None |

### Priority Score (Tests Unlocked / Hours)

1. **T0-001:** 500+ / 0.03 hr = **16,666 tests/hr** ← Do first!
2. **T1-002:** 3 / 0.08 hr = 37 tests/hr
3. **T1-001:** 5 / 0.25 hr = 20 tests/hr
4. **T2-007:** 3 / 2 hr = 1.5 tests/hr
5. **T2-001-006:** 5 / 4 hr = 1.25 tests/hr each

---

## CI/CD Configuration

### GitHub Actions Workflow

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  OPENAI_BASE_URL: https://api.deepseek.com
  OPENAI_MODEL: deepseek-chat
  DATABASE_URL: sqlite:///kosmos_test.db

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev,test]"
      - run: pytest tests/unit -v --tb=short

  e2e-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev,test]"
      - run: pytest tests/e2e -v --timeout=300
```

---

## Success Metrics

### Phase 1 Complete When:
- [ ] `pytest tests/ --collect-only` shows 0 errors
- [ ] All 2,118+ tests collectible

### Phase 2 Complete When:
- [ ] 7 skipped unit test files restored
- [ ] All restored tests passing

### Phase 3 Complete When:
- [ ] E2E tests run with DeepSeek
- [ ] Full research workflow completes

### Production Ready When:
- [ ] >95% unit tests passing
- [ ] >80% E2E tests passing (excluding optional service tests)
- [ ] Full workflow validated
- [ ] CI/CD pipeline green

---

*Implementation plan regenerated to reflect actual codebase state*
*Previous plan based on outdated dependency report*
