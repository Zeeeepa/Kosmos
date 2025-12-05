# Kosmos E2E Dependency Remediation Checklist

**Generated:** 2025-11-26 (Updated)
**Target:** Production-ready E2E testing
**Total Tests:** 2,118 (43 files blocked)
**Current State:** API keys configured, Docker running

---

## Progress Overview

| Milestone | Status | Tests Unlocked | Effort |
|-----------|--------|----------------|--------|
| M0: Fix Collection Errors | ⬜ Not Started | +500 | 2 min |
| M1: Restore Unit Tests | ⬜ Not Started | +35 | 4-8 hr |
| M2: Runtime Error Fixes | ⬜ Not Started | +?? | 2-4 hr |
| M3: E2E Validation | ⬜ Not Started | Validate | 1-2 hr |

**Legend:** ⬜ Not Started | 🔄 In Progress | ✅ Complete

---

## Milestone 0: Fix Collection Errors (2 minutes)

**Goal:** Enable collection of all 43 blocked test files
**Tests Unlocked:** ~500+ tests
**This is the highest-ROI fix possible!**

### 0.1 Add Missing Pytest Markers

- [ ] **Edit `pytest.ini`**

  Add these 3 lines to the `markers` section:
  ```ini
      requirement: Requirement ID marker for traceability
      category: Test category (data_analysis, scientific, etc.)
      priority: Priority level (MUST, SHOULD, MAY)
  ```

### 0.2 Verification

```bash
# Before fix (current state):
pytest tests/requirements --collect-only 2>&1 | grep "errors"
# Expected: "43 errors during collection"

# After fix:
pytest tests/requirements --collect-only -q
# Expected: "500+ tests collected"
```

- [ ] Collection errors resolved (0 errors)
- [ ] 500+ tests now collectible

**Mark M0 complete when:** `pytest tests/ --collect-only` shows 0 errors

---

## Milestone 1: Restore Skipped Unit Tests (4-8 hours)

**Goal:** Remove module-level skips from 7 test files
**Tests Unlocked:** ~35 tests

### 1.1 test_vector_db.py (Priority 1)

- [ ] **Remove skip statement**
  ```bash
  # File: tests/unit/knowledge/test_vector_db.py
  # Remove line 2: pytest.skip('Test needs API update...', allow_module_level=True)
  ```

- [ ] **Run and identify failures**
  ```bash
  pytest tests/unit/knowledge/test_vector_db.py -v --tb=short
  ```

- [ ] **Fix each failure** (update mocks/expectations)

- [ ] **Verify all pass**
  ```bash
  pytest tests/unit/knowledge/test_vector_db.py -v
  # Expected: all tests pass
  ```

### 1.2 test_embeddings.py (Priority 2)

- [ ] Remove skip statement (line 2)
- [ ] Run and identify failures
- [ ] Fix each failure
- [ ] Verify all pass

### 1.3 test_refiner.py (Priority 3)

- [ ] Remove skip statement (line 2)
- [ ] Run and identify failures
- [ ] Fix each failure
- [ ] Verify all pass

### 1.4 test_arxiv_client.py (Priority 4)

- [ ] Remove skip statement (line 2)
- [ ] Run and identify failures
- [ ] Fix each failure
- [ ] Verify all pass

### 1.5 test_pubmed_client.py (Priority 5)

- [ ] Remove skip statement (line 2)
- [ ] Run and identify failures
- [ ] Fix each failure
- [ ] Verify all pass

### 1.6 test_semantic_scholar.py (Priority 6)

- [ ] Remove skip statement (line 2)
- [ ] Run and identify failures
- [ ] Fix each failure
- [ ] Verify all pass

### 1.7 test_profiling.py (Priority 7)

- [ ] Remove skip statement (line 2)
- [ ] Run and identify failures
- [ ] Fix each failure
- [ ] Verify all pass

### M1 Verification

```bash
# Check no more module-level skips
grep -r "pytest.skip.*allow_module_level" tests/unit/
# Expected: no results

# Run all formerly-skipped files
pytest tests/unit/knowledge/test_vector_db.py \
       tests/unit/knowledge/test_embeddings.py \
       tests/unit/hypothesis/test_refiner.py \
       tests/unit/literature/test_arxiv_client.py \
       tests/unit/literature/test_pubmed_client.py \
       tests/unit/literature/test_semantic_scholar.py \
       tests/unit/core/test_profiling.py \
       -v --tb=short
```

- [ ] All 7 files have skip removed
- [ ] All tests in these files pass

---

## Milestone 2: Fix Runtime Errors (2-4 hours)

**Goal:** Fix test failures discovered during runs

### 2.1 Run Full Unit Test Suite

```bash
pytest tests/unit -v --tb=short 2>&1 | tee unit_test_results.log
```

### 2.2 Categorize Failures

```bash
# Count failures
grep -c "FAILED" unit_test_results.log

# List failed tests
grep "FAILED" unit_test_results.log
```

### 2.3 Fix Categories

- [ ] **Import errors** - Missing dependencies or circular imports
- [ ] **Mock issues** - Outdated mock setups
- [ ] **Assertion failures** - Updated return values
- [ ] **Timeout issues** - Async test timeouts

### M2 Verification

```bash
pytest tests/unit --tb=no -q
# Expected: >95% pass rate
```

---

## Milestone 3: E2E Validation (1-2 hours)

**Goal:** Verify E2E tests work with DeepSeek API

### 3.1 Environment Check

```bash
# Verify API configuration
env | grep -E "OPENAI"
# Expected:
# OPENAI_API_KEY=sk-REDACTED-key-revoked
# OPENAI_BASE_URL=https://api.deepseek.com
# OPENAI_MODEL=deepseek-chat
```

### 3.2 Run E2E Tests

```bash
pytest tests/e2e -v --tb=short --timeout=300
```

### 3.3 Expected Results

| Test | Expected Status |
|------|-----------------|
| test_system_sanity.py | Pass (with LLM) |
| test_autonomous_research.py | Pass (mock mode) |
| test_full_research_workflow.py | Pass (with DeepSeek) |

### 3.4 Document Skips

Tests that skip due to missing optional services (OK):
- [ ] Knowledge graph tests (Neo4j not configured)
- [ ] Redis cache tests (disabled)

### M3 Verification

```bash
pytest tests/e2e --tb=no -q
# Expected: >80% pass, some skips for optional services
```

---

## Quick Reference: Commands

```bash
# Check collection status
pytest tests/ --collect-only -q 2>&1 | tail -5

# Run unit tests
pytest tests/unit -v --tb=short

# Run E2E tests
pytest tests/e2e -v --timeout=300

# Run with coverage
pytest tests/ --cov=kosmos --cov-report=term-missing

# Check for skipped files
grep -r "pytest.skip.*allow_module_level" tests/

# View test results summary
pytest tests/ --tb=no -q
```

---

## Environment Variables Reference

Current configuration (from `.env`):

```bash
# LLM Provider (working)
OPENAI_API_KEY=sk-REDACTED-key-revoked
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat

# Database (working)
DATABASE_URL=sqlite:///./kosmos.db

# Cache (disabled)
ENABLE_REDIS_CACHE=false

# Optional services (not configured)
# NEO4J_URI=bolt://localhost:7687
# REDIS_URL=redis://localhost:6379/0
```

---

## Fix → Test Unlock Summary

| Fix | Effort | Tests | Priority |
|-----|--------|-------|----------|
| Add pytest markers | 2 min | +500 | **DO FIRST** |
| test_vector_db.py | 4 hr | +5 | High |
| test_embeddings.py | 4 hr | +5 | High |
| test_refiner.py | 4 hr | +5 | High |
| test_arxiv_client.py | 4 hr | +5 | Medium |
| test_pubmed_client.py | 4 hr | +5 | Medium |
| test_semantic_scholar.py | 4 hr | +5 | Medium |
| test_profiling.py | 2 hr | +3 | Low |

**Total after all fixes:** 2,118+ tests collectible, >95% passing

---

## Progress Log

### [Date: 2025-11-26]
- **Completed:** Regenerated all 3 E2E workflow documents with accurate state
- **Discovered:** 43 collection errors caused by missing pytest markers
- **Discovered:** 7 unit test files skipped (API mismatch)
- **Next:** Apply M0 fix (2 min marker addition)

### [Date: ____-__-__]
- **Completed:**
- **Blocked by:**
- **Next:**

---

## Final Checklist

Before declaring production-ready:

- [ ] M0: 0 collection errors
- [ ] M1: 7 skipped files restored
- [ ] M2: Unit tests >95% passing
- [ ] M3: E2E tests validated with DeepSeek
- [ ] Documentation updated with final state
- [ ] CI/CD pipeline configured

---

*Checklist regenerated to reflect actual codebase state as of 2025-11-26*
