# Resume Prompt - Post Compaction

## Context

You are resuming work on the Kosmos project after a context compaction. The previous sessions implemented **11 paper implementation gaps** (3 BLOCKER + 5 Critical + 3 High).

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

### Key Files Created/Modified (Recent)

| File | Changes |
|------|---------|
| `kosmos/execution/figure_manager.py` | **NEW** - FigureManager class |
| `kosmos/execution/code_generator.py` | Added figure generation to 4 templates |
| `kosmos/world_model/artifacts.py` | Added figure_paths, figure_metadata to Finding |
| `tests/unit/execution/test_figure_manager.py` | **NEW** - 35 unit tests |
| `tests/integration/test_figure_generation.py` | **NEW** - 19 integration tests |

## Remaining Work (6 gaps)

### Implementation Order

| Phase | Order | Issue | Description | Status |
|-------|-------|-------|-------------|--------|
| 1 | 1 | #59 | h5ad/Parquet Data Formats | ✅ Complete |
| 1 | 2 | #69 | R Language Support | ✅ Complete |
| 2 | 3 | #60 | Figure Generation | ✅ Complete |
| 2 | 4 | #61 | Jupyter Notebook Generation | **Next** |
| 3 | 5 | #70 | Null Model Statistical Validation | Pending |
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
- `docs/PAPER_IMPLEMENTATION_GAPS.md` - 17 tracked gaps (11 complete)
- `/home/jim/.claude/plans/peppy-floating-feather.md` - Full implementation plan
- GitHub Issues #54-#70 - Detailed tracking

## Quick Verification Commands

```bash
# Verify figure generation
python -c "
from kosmos.execution.figure_manager import FigureManager, FigureMetadata
from kosmos.world_model.artifacts import Finding

# Test FigureManager
fm = FigureManager(artifacts_dir='/tmp/test', use_visualizer=False)
print('Plot type for t_test:', fm.select_plot_type('t_test'))
print('Plot type for correlation:', fm.select_plot_type('correlation'))

# Test Finding with figure_paths
f = Finding(finding_id='f1', cycle=1, task_id=1, summary='test', statistics={}, figure_paths=['path/fig.png'])
print('Finding figure_paths:', f.figure_paths)
print('All imports successful')
"

# Run tests
python -m pytest tests/unit/execution/test_figure_manager.py -v --tb=short
python -m pytest tests/integration/test_figure_generation.py -v --tb=short
```

## Resume Command

Start by reading the checkpoint:
```
Read docs/CHECKPOINT.md and docs/PAPER_IMPLEMENTATION_GAPS.md, then continue with the next item: #61 - Jupyter Notebook Generation
```

## Progress Summary

**11/17 gaps fixed (65% complete)**

| Priority | Status |
|----------|--------|
| BLOCKER | 3/3 complete ✅ |
| Critical | 5/5 complete ✅ |
| High | 3/5 complete |
| Medium | 0/2 remaining |
| Low | 0/2 remaining |

## Next Step

Continue with **#61 - Jupyter Notebook Generation**:
- Create `NotebookGenerator` class using nbformat
- Support Python and R kernels
- Embed code cells with outputs and figures
- Save to `artifacts/cycle_N/notebooks/`
- Track total line count
