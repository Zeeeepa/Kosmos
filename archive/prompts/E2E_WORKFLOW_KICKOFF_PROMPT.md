# E2E Testing Workflow Kickoff Prompt

## What This Does

This prompt executes a 3-step workflow to bring Kosmos E2E testing to production state:

```
STEP 1: ANALYZE    →    STEP 2: PLAN    →    STEP 3: EXECUTE
(5-10 min)              (5-10 min)           (5-10 min)

Output:                 Output:              Output:
Dependency Report       Implementation Plan  Remediation Checklist
```

---

## Quick Start

**Full Workflow (All 3 Steps):**
Copy and paste this entire block into Claude Code:

```
@E2E_TESTING_WORKFLOW_GUIDE.md
@e2e_testing_missing_dependencies_report_prompt.md

Execute the complete Kosmos E2E Testing Workflow (all 3 steps in sequence):

**STEP 1 - ANALYZE:** Using the dependency report prompt above, analyze the Kosmos
codebase and generate E2E_TESTING_DEPENDENCY_REPORT.md with:
- All missing dependencies and blocked tests
- Service availability matrix
- Fix sequencing dependencies

**STEP 2 - PLAN:** After Step 1, read @e2e_testing_implementation_prompt.md and
the Step 1 output to generate E2E_TESTING_IMPLEMENTATION_PLAN.md with:
- Phased test implementation plan
- Actual pytest code for priority tests
- Fix → Test Unlock Map (Appendix A)

**STEP 3 - EXECUTE:** After Step 2, read @e2e_dependency_remediation_checklist_prompt.md
and both previous outputs to generate E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md with:
- Milestone-based checklist (M1-M5)
- Copy-paste commands for each fix
- Progress tracking table

Run all 3 steps sequentially. If context gets low, create continuation prompts.
Goal: Generate all 3 output files for bringing E2E testing to production.
```

---

## Individual Steps

### Step 1 Only (Analyze)

```
@e2e_testing_missing_dependencies_report_prompt.md

Execute Step 1 of the E2E testing workflow: Generate E2E_TESTING_DEPENDENCY_REPORT.md
by analyzing the Kosmos codebase for all missing dependencies and blocked tests.
```

### Step 2 Only (Plan) - Requires Step 1 Output

```
@e2e_testing_implementation_prompt.md
@E2E_TESTING_DEPENDENCY_REPORT.md

Execute Step 2 of the E2E testing workflow: Generate E2E_TESTING_IMPLEMENTATION_PLAN.md
based on the dependency report from Step 1.
```

### Step 3 Only (Execute) - Requires Step 1 & 2 Outputs

```
@e2e_dependency_remediation_checklist_prompt.md
@E2E_TESTING_DEPENDENCY_REPORT.md
@E2E_TESTING_IMPLEMENTATION_PLAN.md

Execute Step 3 of the E2E testing workflow: Generate E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md
based on the dependency report (Step 1) and implementation plan (Step 2).
```

---

## Resume From Checkpoint

If a previous run was interrupted, use these continuation prompts:

### Resume Step 2 (Step 1 already done)

```
@STEP2_CONTINUATION_PROMPT.md
```

### Resume Step 3 (Steps 1 & 2 already done)

```
@STEP3_CONTINUATION_PROMPT.md
```

---

## Output Files

After successful execution, you'll have:

| File | Purpose | Size |
|------|---------|------|
| `E2E_TESTING_DEPENDENCY_REPORT.md` | What's broken | ~600 lines |
| `E2E_TESTING_IMPLEMENTATION_PLAN.md` | What to build | ~700 lines |
| `E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md` | How to fix | ~500 lines |

---

## Verification

After the workflow completes:

```bash
# Check all 3 files exist
ls -la E2E_TESTING_DEPENDENCY_REPORT.md \
       E2E_TESTING_IMPLEMENTATION_PLAN.md \
       E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md

# View the checklist milestones
grep "^## Milestone" E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md

# Count action items
grep -c "^\- \[ \]" E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md
```

---

## Next Steps After Workflow

1. Open `E2E_DEPENDENCY_REMEDIATION_CHECKLIST.md`
2. Start with **Milestone 1: Environment Setup**
3. Check off items as you complete them
4. Track progress in the Progress Log section
5. Target: 350+ tests passing, >70% coverage

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Context limit reached | Use continuation prompts (STEP2/STEP3_CONTINUATION_PROMPT.md) |
| Step 2 fails | Ensure E2E_TESTING_DEPENDENCY_REPORT.md exists from Step 1 |
| Step 3 fails | Ensure both Step 1 and Step 2 outputs exist |
| Outdated analysis | Delete outputs and re-run full workflow |

---

## File Dependencies

```
                    ┌───────────────────────┐
                    │ e2e_testing_missing_  │
                    │ dependencies_report_  │
                    │ prompt.md             │
                    └──────────┬────────────┘
                               │
                               ▼
                    ┌───────────────────────┐
                    │ E2E_TESTING_          │
                    │ DEPENDENCY_REPORT.md  │ ◄── Step 1 Output
                    └──────────┬────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      │
┌───────────────────┐  ┌───────────────────┐         │
│ e2e_testing_      │  │ e2e_dependency_   │         │
│ implementation_   │  │ remediation_      │         │
│ prompt.md         │  │ checklist_        │         │
└────────┬──────────┘  │ prompt.md         │         │
         │             └────────┬──────────┘         │
         ▼                      │                    │
┌───────────────────┐           │                    │
│ E2E_TESTING_      │           │                    │
│ IMPLEMENTATION_   │ ◄─────────┼────────────────────┘
│ PLAN.md           │ ◄── Step 2 Output
└────────┬──────────┘           │
         │                      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌───────────────────────┐
         │ E2E_DEPENDENCY_       │
         │ REMEDIATION_          │
         │ CHECKLIST.md          │ ◄── Step 3 Output
         └───────────────────────┘
```

---

*This kickoff prompt was created to streamline the E2E testing workflow.*
*For detailed documentation, see E2E_TESTING_WORKFLOW_GUIDE.md*
