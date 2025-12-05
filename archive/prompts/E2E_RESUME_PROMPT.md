# E2E Testing Resume Prompt

## Quick Context

Copy and paste this into a new Claude Code session to continue the E2E testing work:

---

```
@E2E_CHECKPOINT_20251126.md
@E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md

Continue the E2E testing production readiness work from the checkpoint.

## What's Already Done
1. All 3 E2E workflow documents regenerated with accurate state
2. Collection errors fixed (43 → 0) by adding missing pytest markers
3. Import error fixed in test_phase2_e2e.py
4. Test count: 2,768 tests now collectible

## What Needs To Be Done Now

### Task 1: Restore 7 Skipped Unit Test Files (Priority Order)

For each file below, do:
1. Remove `pytest.skip('Test needs API update...', allow_module_level=True)` at line 2
2. Run: `pytest <file> -v --tb=short`
3. Analyze failures and fix test expectations to match current API
4. Verify all pass before moving to next file

Files to restore (in priority order):
1. tests/unit/knowledge/test_vector_db.py
2. tests/unit/knowledge/test_embeddings.py
3. tests/unit/hypothesis/test_refiner.py
4. tests/unit/literature/test_arxiv_client.py
5. tests/unit/literature/test_pubmed_client.py
6. tests/unit/literature/test_semantic_scholar.py
7. tests/unit/core/test_profiling.py

### Task 2: Fix Any Runtime Errors Discovered

After restoring skipped files, run full suite:
```bash
pytest tests/unit -v --tb=short
```
Fix any failures found.

### Task 3: Validate E2E Tests

```bash
pytest tests/e2e -v --timeout=300
```
Document any remaining skips (OK if due to optional services like Neo4j).

## Success Criteria
- 0 module-level skipped files
- >95% unit tests passing
- E2E tests validated with DeepSeek API

Start with Task 1, file 1 (test_vector_db.py).
```

---

## Alternative: Focused Single-File Prompt

If you want to work on just one file at a time:

```
@E2E_CHECKPOINT_20251126.md

Restore the skipped unit test file: tests/unit/knowledge/test_vector_db.py

Steps:
1. Read the current implementation at kosmos/knowledge/vector_db.py
2. Read the test file tests/unit/knowledge/test_vector_db.py
3. Remove the pytest.skip() at line 2
4. Run tests and identify failures
5. Fix each test to match the current PaperVectorDB API
6. Verify all tests pass

Focus on this one file only. When complete, I'll move to the next.
```

---

## Verification After Resume

After completing all tasks, verify:

```bash
# No more module-level skips
grep -r "pytest.skip.*allow_module_level" tests/unit/
# Expected: no results

# Collection clean
pytest tests/ --collect-only -q 2>&1 | tail -3
# Expected: "2768+ tests collected" with no errors

# Unit tests passing
pytest tests/unit --tb=no -q
# Expected: >95% pass rate

# E2E tests work
pytest tests/e2e -v --timeout=300
# Expected: Most pass, some skip for optional services
```

---

## Key API Changes to Watch For

Based on the import fix we did, common patterns to look for:

| Old Name | New Name | Location |
|----------|----------|----------|
| `VectorDatabase` | `PaperVectorDB` | `kosmos/knowledge/vector_db.py` |
| `ProfileData` | `ProfileResult` | `kosmos/core/profiling.py` |

When restoring tests, check if class/method names have changed in the source.

---

*Resume prompt created: 2025-11-26*
