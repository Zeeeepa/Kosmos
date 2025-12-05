# Step 2: E2E Testing Implementation Plan

## Context

Step 1 of the E2E testing workflow has been completed. The dependency report is available at:
- `E2E_TESTING_DEPENDENCY_REPORT.md`

## Task

Execute Step 2 of the E2E testing workflow:

1. **Read the Step 2 prompt:**
   ```
   @e2e_testing_implementation_prompt.md
   ```

2. **Read the Step 1 output:**
   ```
   @E2E_TESTING_DEPENDENCY_REPORT.md
   ```

3. **Generate the implementation plan** at `E2E_TESTING_IMPLEMENTATION_PLAN.md` with:
   - Phase 1: Immediate Implementation (tests runnable today)
   - Phase 2: Dependency Remediation (what to fix next)
   - Phase 3: Full E2E Coverage
   - Gap Module Test Matrix (status of each of 6 gaps)
   - Test Implementations (actual pytest code)
   - CI/CD Configuration (GitHub Actions workflow)
   - **Appendix A: Fix → Test Unlock Map** (critical for Step 3)

4. **After generating, create continuation prompt for Step 3:**
   Save `STEP3_CONTINUATION_PROMPT.md` for the next session.

## Key Inputs from Step 1

### Critical Blockers (P0)
| Dependency | Status | Blocked Tests |
|------------|--------|---------------|
| ANTHROPIC_API_KEY | Missing | 8+ E2E tests |
| Docker daemon | Not running | 10+ tests |
| Neo4j | Not configured | 5+ tests |

### Module-Level Skip Files (6 files with API mismatch)
- `tests/unit/knowledge/test_vector_db.py`
- `tests/unit/literature/test_arxiv_client.py`
- `tests/unit/literature/test_pubmed_client.py`
- `tests/unit/literature/test_semantic_scholar.py`
- `tests/unit/knowledge/test_embeddings.py`
- `tests/unit/hypothesis/test_refiner.py`

### Tier 1 Quick Wins (< 1 hour)
| Fix ID | Task | Effort | Tests Unlocked |
|--------|------|--------|----------------|
| T1-001 | Set ANTHROPIC_API_KEY | 5 min | 8+ E2E tests |
| T1-002 | Start Docker daemon | 5 min | 10+ execution tests |
| T1-003 | docker compose up -d neo4j | 10 min | 5+ knowledge tests |
| T1-006 | Build sandbox image | 15 min | 6+ sandbox tests |

## Expected Output

`E2E_TESTING_IMPLEMENTATION_PLAN.md` with structure matching `e2e_testing_implementation_prompt.md`.

## Workflow Reference

See `E2E_TESTING_WORKFLOW_GUIDE.md` for the complete 3-step workflow documentation.

---

**To start Step 2, copy this into Claude Code:**

```
@e2e_testing_implementation_prompt.md
@E2E_TESTING_DEPENDENCY_REPORT.md

Execute Step 2 of the E2E testing workflow: Generate E2E_TESTING_IMPLEMENTATION_PLAN.md based on the dependency report from Step 1.

After generating, create STEP3_CONTINUATION_PROMPT.md for the final step.
```
