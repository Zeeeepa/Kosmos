# Step 3: E2E Dependency Remediation Checklist

## Context

Steps 1 and 2 of the E2E testing workflow have been completed:
- `E2E_TESTING_DEPENDENCY_REPORT.md` - Dependency analysis (Step 1)
- `E2E_TESTING_IMPLEMENTATION_PLAN.md` - Implementation plan with test code (Step 2)

## Task

Execute Step 3 of the E2E testing workflow:

1. **Read the Step 3 prompt:**
   ```
   @e2e_dependency_remediation_checklist_prompt.md
   ```

2. **Read the previous step outputs:**
   ```
   @E2E_TESTING_DEPENDENCY_REPORT.md
   @E2E_TESTING_IMPLEMENTATION_PLAN.md
   ```

3. **Generate the remediation checklist** at `E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md` with:
   - Progress Overview (milestone tracking table)
   - Milestone 1: Environment Setup (Python + packages)
   - Milestone 2: Core Services Running (DB, Neo4j, Redis)
   - Milestone 3: All APIs Configured (LLM providers)
   - Milestone 4: Docker Sandbox Ready (Gap 4 execution)
   - Milestone 5: Full E2E Passing (complete coverage)
   - Quick Reference: Environment Variables (.env template)
   - Troubleshooting (common issues + fixes)
   - Progress Log (daily tracking section)

## Key Inputs from Steps 1 & 2

### Fix → Test Unlock Map (from Step 2, Appendix A)

| Fix ID | Description | Effort | Tests Unlocked | Depends On |
|--------|-------------|--------|----------------|------------|
| FIX-001 | Set ANTHROPIC_API_KEY | 5 min | 8 tests | None |
| FIX-002 | Start Docker daemon | 5 min | 10 tests | None |
| FIX-003 | docker compose up -d neo4j | 10 min | 5 tests | FIX-002 |
| FIX-004 | docker compose up -d redis | 5 min | 3 tests | FIX-002 |
| FIX-005 | pip install plotly | 5 min | 2 tests | None |
| FIX-006 | Build sandbox image | 15 min | 6 tests | FIX-002 |
| FIX-007-012 | Update 6 API mismatch test files | 4 hr each | 30 tests | None |
| FIX-014 | Implement CacheManager | 8 hr | 3 tests | None |
| FIX-015 | Complete sandbox implementation | 2-3 days | 8 tests | FIX-006 |

### Fix Sequencing (from Step 1, Section 6.7)

```
LEVEL 0: FIX-001, FIX-002, FIX-005 (no dependencies)
LEVEL 1: FIX-003, FIX-004, FIX-006 (depend on FIX-002)
LEVEL 2: FIX-015 (depends on FIX-006)
LEVEL 3: FIX-007 to FIX-014 (can run in parallel)
```

### Current Test Status

- 273 unit tests passing
- 43 integration tests (many skipped)
- 23 E2E tests (most blocked)
- Target: 350+ tests passing

## Expected Output

`E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md` with:
- Checkbox items for each fix
- Exact commands to copy-paste
- Verification steps after each fix
- Tests unlocked after each milestone
- Progress tracking table

## Workflow Reference

See `E2E_TESTING_WORKFLOW_GUIDE.md` for the complete 3-step workflow documentation.

---

**To start Step 3, copy this into Claude Code:**

```
@e2e_dependency_remediation_checklist_prompt.md
@E2E_TESTING_DEPENDENCY_REPORT.md
@E2E_TESTING_IMPLEMENTATION_PLAN.md

Execute Step 3 of the E2E testing workflow: Generate E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md based on the dependency report (Step 1) and implementation plan (Step 2).

This is the final step - the checklist should be immediately actionable with copy-paste commands.
```
