# Prompt: Create Actionable E2E Testing Implementation Plan

## Context

You have just generated `E2E_TESTING_DEPENDENCY_REPORT.md` which analyzed the Kosmos codebase for missing dependencies, configuration gaps, and environmental requirements. Now use that report to create a **realistic, actionable E2E testing implementation plan** tailored to the current environment state.

---

## Prerequisites

Before running this prompt, ensure you have:
1. Generated `E2E_TESTING_DEPENDENCY_REPORT.md` (via the dependency analysis prompt)
2. Read and understood the dependency report findings

---

## Reference Files to Read

1. **`E2E_TESTING_DEPENDENCY_REPORT.md`** - Your generated dependency analysis (READ FIRST)
2. **`e2e_testing_prompt.md`** - Comprehensive E2E testing context and scenarios
3. **`.claude/skills/kosmos-e2e-testing/SKILL.md`** - E2E testing skill capabilities
4. **`.claude/skills/kosmos-e2e-testing/reference.md`** - Test markers and environment variables

---

## Your Task

Using the dependency report findings, create an E2E testing implementation plan that:

### 1. Acknowledges Current Reality

Based on `E2E_TESTING_DEPENDENCY_REPORT.md`:
- What test tier is currently achievable? (`mock_only`, `api_only`, `partial_e2e`, `full_e2e`)
- Which services are available vs missing?
- Which Python packages have issues?
- What configuration is set vs missing?

### 2. Defines Immediate Actions (Phase 1: This Week)

Create tests that work **right now** with current dependencies:

```markdown
## Phase 1: Tests Runnable Today

### Available Infrastructure
- [ ] List what's working from dependency report

### Immediate Test Implementation
For each test, specify:
- Test file path: `tests/e2e/test_xxx.py`
- Test tier: sanity/smoke/integration/e2e
- Dependencies required: (list only available ones)
- Mock strategy: What to mock for missing dependencies
- Expected outcome: What this validates
```

### 3. Defines Remediation Path (Phase 2: Next Sprint)

Address blockers identified in the dependency report:

```markdown
## Phase 2: Unblock More Tests

### Quick Wins (< 1 day each)
- [ ] Install package X
- [ ] Set environment variable Y
- [ ] Add mock for service Z

### Medium Effort (1-3 days)
- [ ] Set up Docker sandbox
- [ ] Configure Neo4j container
- [ ] Fix API mismatch in test_xxx.py

### Tests Unlocked After Remediation
- List tests that become runnable after each fix
```

### 4. Prioritizes by Gap Module

The 6 gaps are the critical path. For each gap, specify what's testable now vs blocked:

| Gap | Module | Testable Now | Blocked By | Priority |
|-----|--------|--------------|------------|----------|
| 0 | Context Compression | Yes/Partial/No | (dependency) | P0-P2 |
| 1 | State Management | Yes/Partial/No | (dependency) | P0-P2 |
| 2 | Task Generation | Yes/Partial/No | (dependency) | P0-P2 |
| 3 | Agent Integration | Yes/Partial/No | (dependency) | P0-P2 |
| 4 | Execution Environment | Yes/Partial/No | (dependency) | P0-P2 |
| 5 | Discovery Validation | Yes/Partial/No | (dependency) | P0-P2 |

### 5. Provides Concrete Test Code

For the top 3-5 priority tests, provide:

```python
# tests/e2e/test_gap0_compression.py
"""
Gap 0: Context Compression E2E Test
Dependencies: [list from report]
Mocks: [what's mocked due to missing deps]
"""

import pytest
from unittest.mock import Mock, patch

# Conditional imports based on availability
try:
    from kosmos.compression.compressor import ContextCompressor
    HAS_COMPRESSOR = True
except ImportError:
    HAS_COMPRESSOR = False

@pytest.mark.e2e
@pytest.mark.skipif(not HAS_COMPRESSOR, reason="ContextCompressor not available")
async def test_context_compression_basic():
    """Test basic compression functionality"""
    # Implementation based on available dependencies
    pass
```

### 6. Defines Success Metrics

Based on realistic expectations from the dependency report:

```markdown
## Success Metrics

### Phase 1 (Current State)
- [ ] X sanity tests passing
- [ ] Y smoke tests passing
- [ ] Z% of Gap modules have at least 1 E2E test

### Phase 2 (After Remediation)
- [ ] A integration tests passing
- [ ] B E2E tests passing
- [ ] Full research workflow completes (mock mode)

### Phase 3 (Full Infrastructure)
- [ ] Full research workflow completes (real LLM)
- [ ] All 6 gaps tested end-to-end
- [ ] CI/CD pipeline green
```

---

## Output Format

Generate a markdown document saved as **`E2E_TESTING_IMPLEMENTATION_PLAN.md`** with this structure:

```markdown
# Kosmos E2E Testing Implementation Plan

**Generated:** [date]
**Based on:** E2E_TESTING_DEPENDENCY_REPORT.md
**Current Test Tier:** [from report]
**Recommended Provider:** [from report]

## Executive Summary
- Current state in 2-3 sentences
- What's achievable now
- Top 3 blockers to address

## Phase 1: Immediate Implementation
[Tests runnable today with current dependencies]

## Phase 2: Dependency Remediation
[Fixes needed to unlock more tests]

## Phase 3: Full E2E Coverage
[Path to complete coverage]

## Gap Module Test Matrix
[Table showing each gap's test status]

## Test Implementations
[Actual test code for priority tests]

## CI/CD Configuration
[GitHub Actions workflow based on available infrastructure]

## Appendix A: Fix → Test Unlock Map

Structured mapping for use by the remediation checklist (Step 3):

| Fix ID | Fix Description | Effort | Tests Unlocked | Test Count | Depends On |
|--------|-----------------|--------|----------------|------------|------------|
| FIX-001 | Install Ollama + models | 30min | test_llm_*, test_integration_* | 12 | None |
| FIX-002 | Set ANTHROPIC_API_KEY | 5min | test_real_llm_*, test_e2e_* | 15 | None |
| FIX-003 | Start Docker daemon | 10min | test_docker_*, test_sandbox_* | 8 | None |
| FIX-004 | Build sandbox image | 15min | test_execution_*, test_gap4_* | 6 | FIX-003 |
| FIX-005 | Start Neo4j container | 15min | test_graph_*, test_knowledge_* | 5 | FIX-003 |
| FIX-006 | Configure Redis | 10min | test_cache_* | 3 | FIX-003 |
| FIX-007 | Fix arxiv package | 1hr | test_arxiv_*, test_literature_* | 8 | None |
| ... | ... | ... | ... | ... | ... |

**Priority Score Formula:** `Tests Unlocked / Effort Hours`

**Recommended Fix Order:**
1. FIX-002 (highest impact/effort ratio)
2. FIX-001 (enables local testing)
3. FIX-003 → FIX-004 (enables Gap 4)
4. FIX-005, FIX-006 (optional services)
5. FIX-007 (workaround available)

## Appendix B: Dependency Status Reference
[Summary table from E2E_TESTING_DEPENDENCY_REPORT.md]
```

---

## Key Principles

1. **Work with what you have** - Don't plan tests that require unavailable dependencies
2. **Mock strategically** - Use mocks to test logic even when services are missing
3. **Incremental progress** - Each phase should unlock more test coverage
4. **Gap modules are priority** - The 6 gaps are the core of Kosmos
5. **CI-friendly first** - Phase 1 tests should run in CI without external services

---

## Instructions

1. Read `E2E_TESTING_DEPENDENCY_REPORT.md` thoroughly
2. Cross-reference with `e2e_testing_prompt.md` for test scenarios
3. Generate the implementation plan following the structure above
4. Provide working test code for immediate implementation
5. Be realistic - only plan what's achievable with current/planned dependencies

The goal is an **actionable plan you can start implementing today**, not a wishlist of tests that require infrastructure you don't have.
