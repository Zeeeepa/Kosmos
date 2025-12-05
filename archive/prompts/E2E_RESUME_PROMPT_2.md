# E2E Testing Resume Prompt 2

## Quick Context

Copy and paste this into a new Claude Code session to continue the E2E testing work:

---

```
@E2E_CHECKPOINT_20251127.md

Continue the E2E testing production readiness work from the checkpoint.

## What's Already Done
1. All module-level pytest.skip() removed from 7 test files
2. test_vector_db.py fully restored (14/14 pass)
3. test_embeddings.py fully restored (12/12 pass)
4. Source fixes applied to refiner.py and conftest.py
5. Test collection: 2,874 tests, 0 errors

## What Needs To Be Done Now

### Task 1: Fix test_refiner.py (12 Failing Tests)

The Hypothesis model has new validation requirements that break tests:
1. `rationale` field requires minimum 20 characters
2. `id` field is not auto-generated

For each failing test:
1. Find inline Hypothesis() creations with short rationales
2. Extend rationale to 20+ characters
3. Check if test relies on hypothesis.id being auto-generated
4. Run: `pytest tests/unit/hypothesis/test_refiner.py -v --tb=short --no-cov`

### Task 2: Fix test_arxiv_client.py (12 Failing Tests)

ArxivClient API changed - constructor no longer accepts max_results/sort_by:
1. Update TestArxivClientInit to match new `__init__(api_key, cache_enabled)` signature
2. Move max_results/sort_by tests to search method tests
3. Update default assertions (max_results is now 100, not 10)
4. Run: `pytest tests/unit/literature/test_arxiv_client.py -v --tb=short --no-cov`

### Task 3: Install responses Library and Fix test_semantic_scholar.py

```bash
pip install responses
```
Then run: `pytest tests/unit/literature/test_semantic_scholar.py -v --tb=short --no-cov`

### Task 4: Fix Remaining Test Files

Run and fix:
- `pytest tests/unit/literature/test_pubmed_client.py -v --tb=short --no-cov`
- `pytest tests/unit/core/test_profiling.py -v --tb=short --no-cov`

## Success Criteria
- All 7 restored test files passing
- >95% unit tests passing overall
- 0 collection errors
```

---

## Alternative: Fix One File at a Time

If you want to focus on just one file:

```
@E2E_CHECKPOINT_20251127.md

Fix the failing tests in tests/unit/hypothesis/test_refiner.py

Current status: 20/32 tests pass
Root cause: Hypothesis model validation changes

Steps:
1. Read the Hypothesis model: kosmos/models/hypothesis.py
2. Find inline Hypothesis() creations in the test file
3. Update rationale fields to be 20+ characters
4. Handle id field expectations
5. Run tests and fix remaining failures
```

---

## Key API Changes to Watch For

| Component | Old | New |
|-----------|-----|-----|
| Hypothesis.rationale | No minimum | Min 20 chars |
| Hypothesis.id | Auto-generated? | Must be provided or None |
| ArxivClient.__init__ | `(max_results, sort_by)` | `(api_key, cache_enabled)` |
| ResultStatus | `FAILURE` | `FAILED` |
| ExperimentResult | Simple | Requires experiment_id, protocol_id, metadata |

---

## Verification After Completion

```bash
# Full unit test suite
pytest tests/unit -v --tb=no --no-cov

# Check pass rate
pytest tests/unit --tb=no --no-cov -q

# Run E2E tests
pytest tests/e2e -v --timeout=300 --no-cov
```

---

*Resume prompt created: 2025-11-27*
