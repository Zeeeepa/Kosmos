# E2E Testing Workflow Checklist

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                        KOSMOS E2E TESTING WORKFLOW                              ║
║                              Quick Reference                                    ║
╠════════════════════════════════════════════════════════════════════════════════╣
║                                                                                 ║
║  STATUS:  [ ] Not Started   [ ] In Progress   [ ] Complete                      ║
║  DATE:    ____________       DURATION: ~20-30 min                               ║
║                                                                                 ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  KICKOFF COMMAND (paste into Claude Code):                                      ║
║  ──────────────────────────────────────────                                     ║
║                                                                                 ║
║    @E2E_WORKFLOW_KICKOFF_PROMPT.md                                             ║
║                                                                                 ║
╠════════════════════════════════════════════════════════════════════════════════╣
║                                                                                 ║
║  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐                 ║
║  │   STEP 1    │   ──►  │   STEP 2    │   ──►  │   STEP 3    │                 ║
║  │   ANALYZE   │        │    PLAN     │        │   EXECUTE   │                 ║
║  └─────────────┘        └─────────────┘        └─────────────┘                 ║
║       5-10 min              5-10 min               5-10 min                     ║
║                                                                                 ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

---

## Pre-Flight Checks

- [ ] Working directory is `/mnt/c/python/kosmos` (project root)
- [ ] Claude Code is running
- [ ] Codebase is current (`git status` clean or aware of changes)

---

## Step 1: ANALYZE (Dependency Report)

**Input:**  `e2e_testing_missing_dependencies_report_prompt.md`
**Output:** `E2E_TESTING_DEPENDENCY_REPORT.md`

| Task | Status |
|------|--------|
| Run Step 1 prompt | [ ] |
| Output file created | [ ] |
| Review Executive Summary | [ ] |

**Verification:**
```bash
ls -la E2E_TESTING_DEPENDENCY_REPORT.md
head -50 E2E_TESTING_DEPENDENCY_REPORT.md
```

**Key Output Sections:**
- Section 6.6: Dependency → Blocked Tests Matrix
- Section 6.7: Fix Sequencing Dependencies

---

## Step 2: PLAN (Implementation Plan)

**Input:**  `e2e_testing_implementation_prompt.md` + Step 1 output
**Output:** `E2E_TESTING_IMPLEMENTATION_PLAN.md`

| Task | Status |
|------|--------|
| Run Step 2 prompt | [ ] |
| Output file created | [ ] |
| Review Phase 1 tests (runnable today) | [ ] |
| Review Appendix A (Fix → Test Unlock Map) | [ ] |

**Verification:**
```bash
ls -la E2E_TESTING_IMPLEMENTATION_PLAN.md
grep -A 20 "Appendix A" E2E_TESTING_IMPLEMENTATION_PLAN.md
```

**Key Output Sections:**
- Phase 1: Immediate Implementation
- Appendix A: Fix → Test Unlock Map

---

## Step 3: EXECUTE (Remediation Checklist)

**Input:**  `e2e_dependency_remediation_checklist_prompt.md` + Step 1 + Step 2 outputs
**Output:** `E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md`

| Task | Status |
|------|--------|
| Run Step 3 prompt | [ ] |
| Output file created | [ ] |
| Review Milestone 1 tasks | [ ] |
| Begin execution from checklist | [ ] |

**Verification:**
```bash
ls -la E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md
grep -c "^\- \[ \]" E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md  # Count checkboxes
```

**Key Output Sections:**
- Progress Overview (M1-M5 milestones)
- Quick Reference: Environment Variables

---

## Post-Workflow

- [ ] All 3 output files generated
- [ ] Started working through remediation checklist
- [ ] Scheduled next check-in

**Output Files Generated:**
```
✓ E2E_TESTING_DEPENDENCY_REPORT.md     (Step 1 - What's broken)
✓ E2E_TESTING_IMPLEMENTATION_PLAN.md   (Step 2 - What to build)
✓ E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md (Step 3 - How to fix)
```

---

## Quick Commands

```bash
# Run full workflow (paste into Claude Code)
@E2E_WORKFLOW_KICKOFF_PROMPT.md

# Run individual steps
@e2e_testing_missing_dependencies_report_prompt.md   # Step 1
@e2e_testing_implementation_prompt.md                # Step 2
@e2e_dependency_remediation_checklist_prompt.md      # Step 3

# Check if outputs exist
ls -la E2E_TESTING_*.md E2E_DEPENDENCY_*.md

# View progress on remediation checklist
grep "^\- \[x\]" E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md | wc -l  # Completed
grep "^\- \[ \]" E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md | wc -l  # Remaining
```

---

## When to Re-Run

Re-run the workflow when:
- [ ] Significant codebase changes (new modules, removed dependencies)
- [ ] 2+ weeks since last analysis
- [ ] Major test failures after changes
- [ ] Starting fresh on a new environment

**To reset:** Delete the 3 output files and re-run from Step 1.

---

## File Map

```
INPUT FILES (Prompts)                    OUTPUT FILES (Generated)
─────────────────────                    ────────────────────────
e2e_testing_missing_dependencies_        E2E_TESTING_DEPENDENCY_
  report_prompt.md                         REPORT.md

e2e_testing_implementation_              E2E_TESTING_IMPLEMENTATION_
  prompt.md                                PLAN.md

e2e_dependency_remediation_              E2E_DEPENDENCY_REMEDIATION_
  checklist_prompt.md                      CHECKLIST.md

REFERENCE FILES
───────────────
E2E_TESTING_WORKFLOW_GUIDE.md           Full workflow documentation
E2E_WORKFLOW_KICKOFF_PROMPT.md          One-command kickoff
e2e_testing_prompt.md                   Comprehensive system context
```

---

*Last updated: 2025-11-26*
