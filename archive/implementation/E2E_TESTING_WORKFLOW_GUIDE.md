# Kosmos E2E Testing Workflow Guide

**Created:** 2025-11-26
**Purpose:** Guide for bringing Kosmos E2E testing to production state
**Estimated Timeline:** 2-4 weeks depending on infrastructure

---

## Overview

This workflow uses 3 sequential prompts to analyze, plan, and execute E2E testing remediation:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        E2E TESTING WORKFLOW                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: ANALYZE          Step 2: PLAN            Step 3: EXECUTE   │
│  ─────────────────        ────────────────        ────────────────  │
│  What's broken?           What tests to write?    How to fix it?    │
│                                                                     │
│  ┌─────────────┐          ┌─────────────┐         ┌─────────────┐   │
│  │ Dependency  │    ──►   │ Implement.  │   ──►   │ Remediation │   │
│  │ Report      │          │ Plan        │         │ Checklist   │   │
│  └─────────────┘          └─────────────┘         └─────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Step 1: Run dependency analysis prompt
# Input:  e2e_testing_missing_dependencies_report_prompt.md
# Output: E2E_TESTING_DEPENDENCY_REPORT.md

# Step 2: Run implementation planning prompt (immediately after Step 1)
# Input:  e2e_testing_implementation_prompt.md
# Output: E2E_TESTING_IMPLEMENTATION_PLAN.md

# Step 3: Run remediation checklist prompt
# Input:  e2e_dependency_remediation_checklist_prompt.md
# Output: E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md

# Then: Execute the checklist over days/weeks
```

---

## Detailed Workflow

### Step 1: Dependency Analysis

**Prompt File:** `e2e_testing_missing_dependencies_report_prompt.md`

**What It Does:**
- Scans codebase for missing dependencies
- Identifies configuration gaps
- Maps dependencies to blocked tests
- Determines fix sequencing

**Output File:** `E2E_TESTING_DEPENDENCY_REPORT.md`

**Key Sections in Output:**
| Section | Purpose |
|---------|---------|
| Executive Summary | Overview of issues |
| Section 1: Python Package Issues | Missing/broken packages |
| Section 2: External Service Requirements | Docker, Neo4j, Redis, etc. |
| Section 3: Configuration Gaps | Missing environment variables |
| Section 4: API/Implementation Issues | Code mismatches |
| Section 4.5: Service Availability Matrix | Which tests need which services |
| Section 5: Dependency Resolution Strategy | Tiered remediation plan |
| **Section 6.6: Dependency → Blocked Tests Matrix** | Maps each issue to affected tests |
| **Section 6.7: Fix Sequencing Dependencies** | Order of operations |
| Section 7: Test Environment Profiles | Minimal/Integration/Full profiles |

**Do NOT wait to fix issues before proceeding to Step 2.**

---

### Step 2: Implementation Planning

**Prompt File:** `e2e_testing_implementation_prompt.md`

**What It Does:**
- Creates phased testing plan based on current state
- Generates actual test code for immediate implementation
- Maps fixes to tests they unlock
- Calculates priority based on impact/effort

**Input:** Reads `E2E_TESTING_DEPENDENCY_REPORT.md` from Step 1

**Output File:** `E2E_TESTING_IMPLEMENTATION_PLAN.md`

**Key Sections in Output:**
| Section | Purpose |
|---------|---------|
| Executive Summary | Current state + what's achievable |
| Phase 1: Immediate Implementation | Tests runnable TODAY |
| Phase 2: Dependency Remediation | What to fix next |
| Phase 3: Full E2E Coverage | Path to complete coverage |
| Gap Module Test Matrix | Status of each of 6 gaps |
| Test Implementations | Actual pytest code |
| CI/CD Configuration | GitHub Actions workflow |
| **Appendix A: Fix → Test Unlock Map** | Fix IDs, effort, tests unlocked, dependencies |

**Appendix A Structure:**
```
| Fix ID  | Description          | Effort | Tests Unlocked    | Count | Depends On |
|---------|---------------------|--------|-------------------|-------|------------|
| FIX-001 | Install Ollama      | 30min  | test_llm_*        | 12    | None       |
| FIX-002 | Set ANTHROPIC_KEY   | 5min   | test_e2e_*        | 15    | None       |
| FIX-003 | Start Docker        | 10min  | test_docker_*     | 8     | None       |
| FIX-004 | Build sandbox image | 15min  | test_execution_*  | 6     | FIX-003    |
```

---

### Step 3: Remediation Checklist

**Prompt File:** `e2e_dependency_remediation_checklist_prompt.md`

**What It Does:**
- Creates milestone-based execution checklist
- Provides exact commands to copy-paste
- Includes verification steps for each fix
- Tracks progress with checkboxes
- Links fixes to tests they unlock

**Input:** Reads BOTH:
- `E2E_TESTING_DEPENDENCY_REPORT.md` (Step 1)
- `E2E_TESTING_IMPLEMENTATION_PLAN.md` (Step 2)

**Output File:** `E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md`

**Key Sections in Output:**
| Section | Purpose |
|---------|---------|
| Progress Overview | Milestone tracking table |
| Milestone 1: Environment Setup | Python + packages |
| Milestone 2: Core Services Running | DB, Neo4j, Redis |
| Milestone 3: All APIs Configured | LLM providers |
| Milestone 4: Docker Sandbox Ready | Gap 4 execution |
| Milestone 5: Full E2E Passing | Complete coverage |
| Quick Reference: Environment Variables | Copy-paste .env template |
| Troubleshooting | Common issues + fixes |
| Progress Log | Daily tracking section |

---

## Data Flow Between Steps

```
Step 1 Output                         Step 2 Output
─────────────────────────────────     ─────────────────────────────────
E2E_TESTING_DEPENDENCY_REPORT.md      E2E_TESTING_IMPLEMENTATION_PLAN.md

• What's broken                       • Phase 1/2/3 tests
• Section 6.6: Blocked Tests Matrix   • Test code
• Section 6.7: Fix Sequencing         • Appendix A: Fix → Test Unlock Map
                │                                    │
                │                                    │
                └──────────────┬─────────────────────┘
                               │
                               ▼
                     Step 3 Output
                     ─────────────────────────────────
                     E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md

                     • Milestone checkboxes
                     • Exact commands
                     • Tests unlocked (from Step 2)
                     • Fix ordering (from Step 1)
                     • Progress tracking
```

---

## Execution Timeline

### Week 1: Setup & Analysis
```
Day 1:
├── Run Step 1 prompt → E2E_TESTING_DEPENDENCY_REPORT.md
├── Run Step 2 prompt → E2E_TESTING_IMPLEMENTATION_PLAN.md
└── Run Step 3 prompt → E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md

Day 2-3:
├── Complete Milestone 1 (Environment Setup)
├── Run sanity tests to verify
└── Start writing Phase 1 tests from implementation plan

Day 4-5:
├── Complete Milestone 2 (Core Services)
├── Run smoke tests
└── Continue Phase 1 tests
```

### Week 2: Services & APIs
```
Day 6-8:
├── Complete Milestone 3 (APIs Configured)
├── Run integration tests
└── Write Phase 2 tests

Day 9-10:
├── Complete Milestone 4 (Docker Sandbox)
├── Run E2E tests
└── Debug any failures
```

### Week 3-4: Full Coverage
```
Day 11-15:
├── Complete Milestone 5 (Full E2E)
├── Fix remaining test failures
├── Achieve coverage targets
└── Set up CI/CD pipeline

Day 16+:
├── Production validation
├── Documentation cleanup
└── Handoff/maintenance plan
```

---

## File Reference

### Prompt Files (Input)
| File | Purpose | When to Run |
|------|---------|-------------|
| `e2e_testing_missing_dependencies_report_prompt.md` | Analyze dependencies | Step 1 |
| `e2e_testing_implementation_prompt.md` | Create test plan | Step 2 |
| `e2e_dependency_remediation_checklist_prompt.md` | Create fix checklist | Step 3 |

### Generated Files (Output)
| File | Generated By | Purpose |
|------|--------------|---------|
| `E2E_TESTING_DEPENDENCY_REPORT.md` | Step 1 | Analysis reference |
| `E2E_TESTING_IMPLEMENTATION_PLAN.md` | Step 2 | Test implementation guide |
| `E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md` | Step 3 | Daily execution tracker |

### Reference Files (Context)
| File | Purpose |
|------|---------|
| `e2e_testing_prompt.md` | Comprehensive system context (referenced by Step 2) |
| `.claude/skills/kosmos-e2e-testing/SKILL.md` | Skill capabilities |
| `.claude/skills/kosmos-e2e-testing/reference.md` | Environment variables, markers |

---

## FAQ

### Q: Do I need to fix dependencies before running Step 2?
**A: No.** Run Step 2 immediately after Step 1. The implementation plan is designed to work with your current broken state and tells you what to fix in priority order.

### Q: What if I already have some dependencies working?
**A: The prompts will detect this.** Working items will be marked as OK in the dependency report, and the checklist will skip them.

### Q: Can I run steps in parallel?
**A: No.** Each step requires output from the previous step:
- Step 2 reads Step 1's output
- Step 3 reads both Step 1 and Step 2's outputs

### Q: How do I track progress over weeks?
**A: Use the checklist.** `E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md` has:
- Checkbox items to mark complete
- Progress Log section for daily notes
- Milestone status table

### Q: What if the codebase changes during remediation?
**A: Re-run Step 1** periodically to get updated dependency status. You may need to regenerate Step 2 and 3 if significant changes occurred.

---

## Skill Integration

The E2E testing skill can auto-generate some reports:

```bash
# Quick dependency check (alternative to full Step 1)
cd .claude/skills/kosmos-e2e-testing
python -c "from lib.report_generator import generate_dependency_report; generate_dependency_report()"

# Check infrastructure status
./scripts/health-check.sh

# Run tests by tier
./scripts/run-tests.sh sanity    # ~30s
./scripts/run-tests.sh smoke     # ~2min
./scripts/run-tests.sh e2e       # ~10min
./scripts/run-tests.sh full      # ~20min
```

---

## Success Criteria

### Milestone Completion
- [ ] M1: Environment Setup - sanity tests pass
- [ ] M2: Core Services - smoke tests pass
- [ ] M3: APIs Configured - integration tests pass
- [ ] M4: Docker Sandbox - E2E tests pass
- [ ] M5: Full Coverage - all tests pass, >70% coverage

### Final Validation
- [ ] `kosmos run "test question" --cycles 1` completes
- [ ] All 6 gap modules tested
- [ ] CI/CD pipeline configured and green
- [ ] Documentation updated

---

## Support

- **Skill Documentation:** `.claude/skills/kosmos-e2e-testing/SKILL.md`
- **Troubleshooting:** `.claude/skills/kosmos-e2e-testing/SKILL.md#troubleshooting`
- **Known Issues:** `.claude/skills/kosmos-e2e-testing/SKILL.md#known-issues--limitations`

---

*This workflow guide was generated alongside the E2E testing prompts on 2025-11-26.*
