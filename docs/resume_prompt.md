# Resume Prompt - Post Compaction

## Context

You are resuming work on the Kosmos project after a context compaction. The previous sessions implemented **12 paper implementation gaps** (3 BLOCKER + 5 Critical + 4 High).

## What Was Done

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

### Key Files Created/Modified (Recent)

| File | Changes |
|------|---------|
| `kosmos/execution/notebook_generator.py` | **NEW** - NotebookGenerator class (530+ lines) |
| `kosmos/world_model/artifacts.py` | Added notebook_metadata field to Finding |
| `tests/unit/execution/test_notebook_generator.py` | **NEW** - 44 unit tests |
| `tests/integration/test_notebook_generation.py` | **NEW** - 21 integration tests |

## Remaining Work (5 gaps)

### Implementation Order

| Phase | Order | Issue | Description | Status |
|-------|-------|-------|-------------|--------|
| 2 | 3 | #60 | Figure Generation | ✅ Complete |
| 2 | 4 | #61 | Jupyter Notebook Generation | ✅ Complete |
| 3 | 5 | #70 | Null Model Statistical Validation | **Next** |
| 3 | 6 | #63 | Failure Mode Detection | Pending |
| 4 | 7 | #62 | Code Line Provenance | Pending |
| 5 | 8 | #64 | Multi-Run Convergence | Pending |
| 5 | 9 | #65 | Paper Accuracy Validation | Pending |

### Testing Requirements

- All tests must pass (no skipped tests except environment-dependent)
- Mock tests must be accompanied by real-world tests
- Do not proceed until current task is fully working

## Key Documentation

- `docs/CHECKPOINT.md` - Full session summary
- `docs/PAPER_IMPLEMENTATION_GAPS.md` - 17 tracked gaps (12 complete)
- `/home/jim/.claude/plans/peppy-floating-feather.md` - Full implementation plan
- GitHub Issues #54-#70 - Detailed tracking

## Quick Verification Commands

```bash
# Verify notebook generation
python -c "
from kosmos.execution.notebook_generator import NotebookGenerator, NotebookMetadata
from kosmos.world_model.artifacts import Finding

# Test NotebookGenerator
gen = NotebookGenerator(artifacts_dir='/tmp/test')
print('Plot type for t_test:', gen.get_notebook_path(1, 1, 't_test'))

# Test Finding with notebook_metadata
f = Finding(finding_id='f1', cycle=1, task_id=1, summary='test', statistics={},
            notebook_path='path/nb.ipynb', notebook_metadata={'kernel': 'python3'})
print('Finding notebook_metadata:', f.notebook_metadata)
print('All imports successful')
"

# Run tests
python -m pytest tests/unit/execution/test_notebook_generator.py -v --tb=short
python -m pytest tests/integration/test_notebook_generation.py -v --tb=short
```

## Resume Command

Start by reading the checkpoint:
```
Read docs/CHECKPOINT.md and docs/PAPER_IMPLEMENTATION_GAPS.md, then continue with the next item: #70 - Null Model Statistical Validation
```

## Progress Summary

**12/17 gaps fixed (71% complete)**

| Priority | Status |
|----------|--------|
| BLOCKER | 3/3 complete ✅ |
| Critical | 5/5 complete ✅ |
| High | 4/5 complete |
| Medium | 0/2 remaining |
| Low | 0/2 remaining |

## Next Step

Continue with **#70 - Null Model Statistical Validation**:
- Create `NullModelValidator` class for permutation testing
- Implement shuffle strategies (column, row, label)
- Calculate p-values from permutation distribution
- Integrate with ScholarEval validation framework
- Flag findings that persist in noise (false positives)
