# Resume Prompt - Post Compaction

## Context

You are resuming work on the Kosmos project after a context compaction. The previous sessions implemented **15 paper implementation gaps** (3 BLOCKER + 5 Critical + 5 High + 2 Medium). The most recent session fixed test suite issues and added real data validation tests.

## What Was Done

### Last Session (Test Suite Maintenance)

Fixed test failures and added real data tests:

| File | Fix |
|------|-----|
| `kosmos/execution/statistics.py` | numpy.bool_ → Python bool conversion |
| `tests/unit/execution/test_statistics.py` | Cohen's d boundary, Bonferroni expected values, normality checks |
| `tests/unit/execution/test_sandbox.py` | Docker exception type mocking |
| `tests/unit/execution/test_result_collector.py` | Pydantic V2 fixtures, db mocking |
| `tests/integration/execution/test_statistics_real_data.py` | **NEW** - 15 real data tests |

Also created GitHub issue #72 for API response streaming.

### All Fixed Issues

| Issue | Description | Implementation |
|-------|-------------|----------------|
| #66 | CLI Deadlock | Full async refactor of message passing |
| #67 | SkillLoader | Domain-to-bundle mapping fixed |
| #68 | Pydantic V2 | Model config migration complete |
| #54 | Self-Correcting Code Execution | Enhanced RetryStrategy with 11 error handlers + LLM repair |
| #55 | World Model Update Categories | UpdateType enum (CONFIRMATION/CONFLICT/PRUNING) + conflict detection |
| #56 | 12-Hour Runtime Constraint | `max_runtime_hours` config + runtime tracking in ResearchDirector |
| #57 | Parallel Task Execution | Changed `max_concurrent_experiments` default from 4 to 10 |
| #58 | Agent Rollout Tracking | New RolloutTracker class + integration in ResearchDirector |
| #59 | h5ad/Parquet Data Formats | `DataLoader.load_h5ad()` and `load_parquet()` methods |
| #69 | R Language Execution | `RExecutor` class + Docker image with TwoSampleMR |
| #60 | Figure Generation | `FigureManager` class + code template integration |
| #61 | Jupyter Notebook Generation | `NotebookGenerator` class + nbformat integration |
| #70 | Null Model Statistical Validation | `NullModelValidator` class + ScholarEval integration |
| #63 | Failure Mode Detection | `FailureDetector` class (over-interp, invented metrics, rabbit hole) |
| #62 | Code Line Provenance | `CodeProvenance` class + hyperlinks to notebook cells |

### Key Files Created/Modified (Recent)

| File | Changes |
|------|---------|
| `kosmos/execution/provenance.py` | CodeProvenance, CellLineMapping (~280 lines) |
| `kosmos/execution/statistics.py` | Fixed numpy.bool_ issue |
| `tests/integration/execution/test_statistics_real_data.py` | **NEW** - 15 real data tests |

## Remaining Work (2 gaps)

### Implementation Order

| Phase | Order | Issue | Description | Status |
|-------|-------|-------|-------------|--------|
| 4 | 7 | #62 | Code Line Provenance | ✅ Complete |
| 5 | 8 | #64 | Multi-Run Convergence | **Next** |
| 5 | 9 | #65 | Paper Accuracy Validation | Pending |

### Testing Requirements

- All tests must pass (no skipped tests except environment-dependent)
- Mock tests must be accompanied by real-world tests
- Do not proceed until current task is fully working

## Key Documentation

- `docs/CHECKPOINT.md` - Full session summary
- `docs/PAPER_IMPLEMENTATION_GAPS.md` - 17 tracked gaps (15 complete)
- GitHub Issues #54-#72 - Detailed tracking

## Quick Verification Commands

```bash
# Verify test fixes
python -m pytest tests/unit/execution/ -v --tb=short

# Run real data statistical tests
python -m pytest tests/integration/execution/test_statistics_real_data.py -v

# Check imports
python -c "
from kosmos.execution import CodeProvenance, CellLineMapping
from kosmos.execution.statistics import StatisticalValidator
from kosmos.validation.null_model import NullModelValidator
from kosmos.validation.failure_detector import FailureDetector
print('All imports successful')
"
```

## Resume Command

Start by reading the checkpoint and checking issue status:
```
Read docs/CHECKPOINT.md and docs/PAPER_IMPLEMENTATION_GAPS.md, then continue with the next item: #64 - Multi-Run Convergence Framework
```

## Progress Summary

**15/17 gaps fixed (88% complete)**

| Priority | Status |
|----------|--------|
| BLOCKER | 3/3 complete ✅ |
| Critical | 5/5 complete ✅ |
| High | 5/5 complete ✅ |
| Medium | 2/2 complete ✅ |
| Low | 0/2 remaining |

## Test Summary

**Total Tests: 3451**

Key test files for recent work:
- `tests/unit/execution/test_statistics.py` - 37 tests
- `tests/unit/execution/test_sandbox.py` - 22 tests
- `tests/unit/execution/test_result_collector.py` - 26 tests
- `tests/integration/execution/test_statistics_real_data.py` - 15 tests

## Next Step

Continue with **#64 - Multi-Run Convergence Framework**:
- Implement `EnsembleRunner.run(n_runs, research_objective)` function
- Calculate convergence metrics across runs
- Report showing findings that appeared in N/M runs
- Non-deterministic validation through replication

### Paper Reference (Section 5)
> "Each research question was run five times with different random seeds"
> "Statistical tests were applied to compare the AI scientist's conclusions to ground truth"

### Implementation Approach

1. Create `kosmos/validation/convergence.py` with:
   - `EnsembleRunner` class to manage multiple runs
   - `ConvergenceMetrics` dataclass for cross-run statistics
   - `run_ensemble(n_runs, objective, seeds)` method

2. Track per-finding:
   - Appearance count across runs (N/M)
   - Statistical consistency (effect sizes, p-values)
   - Convergence score based on replication

3. Generate convergence report:
   - Findings ranked by replication consistency
   - Highlight findings that appear in all runs vs. some
   - Flag unstable findings (high variance across runs)
