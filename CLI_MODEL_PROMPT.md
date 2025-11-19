# CLI Model Bug-Fixing Instructions - Kosmos AI Scientist v0.2.0

**Role:** CLI-based Claude Code Model
**Task:** Fix 29 bugs from CLI_BASED_BUGS.md
**Working Directory:** `../kosmos-cli-fixes/`
**Coordination:** You will work in parallel with a Web model fixing different bugs

## CRITICAL: READ THIS FIRST

You are working alongside another AI model (Web) that is fixing different bugs simultaneously. To prevent merge conflicts:

1. **YOU OWN THESE FILES EXCLUSIVELY** (no conflicts possible):
   - `kosmos/knowledge/embeddings.py` (Bug #13)
   - `kosmos/knowledge/vector_db.py` (Bug #14)
   - `kosmos/knowledge/graph_builder.py` (Bug #21)
   - `kosmos/literature/pubmed_client.py` (Bugs #16, #17)
   - `kosmos/literature/semantic_scholar.py` (Bug #18)
   - `kosmos/cli/main.py` (Bug #19)
   - `kosmos/agents/research_director.py` (Bug #29)
   - `kosmos/execution/sandbox.py` (Bugs #15, #30)
   - `kosmos/core/providers/anthropic.py` (Bugs #10, #11)
   - `kosmos/core/providers/openai.py` (Bug #12)
   - `tests/conftest.py` (Bug #7)
   - Test files for imports (Bugs #5, #6)

2. **SHARED FILES REQUIRING COORDINATION**:
   - `kosmos/world_model/simple.py` - WAIT FOR WEB FIRST (Your bugs #2, #3, #4)
   - `kosmos/core/llm.py` - WAIT FOR WEB FIRST (Your bugs #8, #9)
   - `kosmos/execution/result_collector.py` - YOU FIX FIRST (Bug #1), then Web, then you (Bug #31)
   - `kosmos/cli/commands/run.py` - Can work independently (Bug #20)

## Setup Instructions

### Step 1: Create Git Worktree

```bash
# From the main Kosmos directory
cd /mnt/c/python/Kosmos
git fetch origin main

# Create your dedicated worktree
git worktree add ../kosmos-cli-fixes --detach origin/main
cd ../kosmos-cli-fixes

# Create your working branch
git checkout -b cli-bugfix-$(date +%Y%m%d-%H%M%S)
git push -u origin HEAD
```

### Step 2: Verify Setup

```bash
# Confirm you're in the correct worktree
pwd  # Should show: /mnt/c/python/kosmos-cli-fixes

# Confirm correct branch
git branch --show-current  # Should show: cli-bugfix-[timestamp]

# Confirm clean state
git status  # Should show: nothing to commit, working tree clean

# Verify test environment
pytest --version
poetry show | grep pytest
```

## Phase 1: Non-Conflicting Fixes (Do These First)

These can be done immediately without any coordination:

### 1.1 Test Import Fixes (Critical)

```bash
# Bug #5: Broken Import - ParallelExecutionResult
# File: tests/integration/test_parallel_execution.py
# Find correct import: python -c "from kosmos.execution.parallel import *; print(dir())"
# Fix import statement
# Test: pytest tests/integration/test_parallel_execution.py::test_imports -v

# Bug #6: Broken Import - EmbeddingGenerator
# File: tests/integration/test_phase2_e2e.py
# Find correct import: python -c "from kosmos.knowledge.embeddings import *; print(dir())"
# Fix import statement
# Test: pytest tests/integration/test_phase2_e2e.py::test_imports -v

# Bug #7: Test Contamination - Reset Functions
# File: tests/conftest.py (lines 306-321)
# Remove try/except, properly import or implement reset functions
# Test: pytest tests/ --collect-only
# Commit: "Fix test imports and conftest reset functions (Bugs #5-7)"
```

### 1.2 Knowledge Module Fixes

```bash
# Bug #13: NoneType Embeddings Model
# File: kosmos/knowledge/embeddings.py (lines 112-116)
# Add initialization check:
if self.model is None:
    self._initialize_model()
if self.model is None:
    raise RuntimeError("Failed to initialize embeddings model")
# Test: pytest tests/unit/knowledge/test_embeddings.py -v
# Commit: "Fix embeddings model initialization checks (Bug #13)"

# Bug #14: NoneType Vector DB Collection
# File: kosmos/knowledge/vector_db.py (lines 170-175, 216-220, 340)
# Add null checks before collection access
# Test: pytest tests/unit/knowledge/test_vector_db.py -v
# Commit: "Fix vector DB collection null checks (Bug #14)"

# Bug #21: Uninitialized Vector DB in Graph Builder
# File: kosmos/knowledge/graph_builder.py (lines 68-71, 375)
# Ensure vector_db initialized in __init__ or lazy init
# Test: pytest tests/unit/knowledge/test_graph_builder.py -v
# Commit: "Fix graph builder vector DB initialization (Bug #21)"
```

### 1.3 Literature API Fixes

```bash
# Bug #16: PubMed API KeyError
# File: kosmos/literature/pubmed_client.py (line 146)
# Add validation:
if 'IdList' not in response:
    return []
# Test: pytest tests/unit/literature/test_pubmed_client.py::test_empty_response -v

# Bug #17: PubMed API IndexError
# File: kosmos/literature/pubmed_client.py (line 253)
# Check array bounds before access
# Test: pytest tests/unit/literature/test_pubmed_client.py::test_no_results -v

# Bug #18: Semantic Scholar Type Mismatch
# File: kosmos/literature/semantic_scholar.py (line 357)
# Type check: isinstance(result, dict) before .get()
# Test: pytest tests/integration/test_semantic_scholar_api.py -v
# Commit: "Fix literature API response validation (Bugs #16-18)"
```

### 1.4 CLI and Execution Fixes

```bash
# Bug #19: Database Not Initialized
# File: kosmos/cli/main.py (lines 242-245)
# Ensure database init before use:
if not db.is_initialized():
    db.init()
# Test: python -m kosmos.cli.main --help
# Commit: "Fix CLI database initialization (Bug #19)"

# Bug #15: Windows Path Handling
# File: kosmos/execution/sandbox.py (lines 226-233)
# Fix Docker volume paths for Windows:
if platform.system() == 'Windows':
    path = path.replace('\\', '/').replace('C:', '/mnt/c')
# Test: pytest tests/integration/test_sandbox.py::test_windows_paths -v

# Bug #30: Exception Handling Too Broad
# File: kosmos/execution/sandbox.py (lines 286-296)
# Separate timeout from other exceptions
# Test: pytest tests/unit/execution/test_sandbox_errors.py -v
# Commit: "Fix sandbox path handling and exceptions (Bugs #15, #30)"

# Bug #29: asyncio.run() in Async Context
# File: kosmos/agents/research_director.py (lines 1292-1294, 1348-1350)
# Check event loop:
if asyncio.get_event_loop().is_running():
    await coroutine()
else:
    asyncio.run(coroutine())
# Test: pytest tests/unit/agents/test_research_director.py -v
# Commit: "Fix async execution context checks (Bug #29)"
```

### 1.5 Provider Response Validation

```bash
# Bug #10-11: Anthropic Response Validation
# File: kosmos/core/providers/anthropic.py (lines 240, 360)
# Add bounds checking:
if not response.choices or len(response.choices) == 0:
    raise LLMError("Empty response from Anthropic API")
content = response.choices[0].message.content

# Bug #12: OpenAI Response Validation
# File: kosmos/core/providers/openai.py (lines 186, 297)
# Same bounds checking pattern
# Test all: pytest tests/unit/core/providers/ -v
# Commit: "Add LLM provider response validation (Bugs #10-12)"
```

### 1.6 Test Fixture Fixes

```bash
# Bugs #22-28: Model Field Discovery
# First, discover correct field names:
python -c "from kosmos.models import Hypothesis; print(Hypothesis.__fields__)"
python -c "from kosmos.models import VariableResult; print(VariableResult.__fields__)"
python -c "from kosmos.models import ExperimentProtocol; print(ExperimentProtocol.__fields__)"
python -c "from kosmos.models import ResourceRequirements; print(ResourceRequirements.__fields__)"
python -c "from kosmos.models import ExperimentType; print(list(ExperimentType))"

# Then fix test files based on discoveries:
# - tests/integration/test_analysis_pipeline.py
# - tests/unit/agents/test_data_analyst.py
# Test: pytest tests/integration/test_analysis_pipeline.py -v
# Commit: "Fix test fixture model fields (Bugs #22-28)"
```

## Phase 2: Coordinated Fixes (CRITICAL TIMING)

### 2.1 Result Collector - YOU GO FIRST

```bash
# Create critical branch immediately
git checkout -b cli-critical-result-collector

# Bug #1: Database Operation Arguments
# File: kosmos/execution/result_collector.py (lines 441-448)
# Add missing session and id parameters:
db_result = db_ops.create_result(
    session=self.db_session,  # Add this
    id=result.id,             # Add this
    experiment_id=result.experiment_id,
    # ... rest of parameters
)

# Test thoroughly:
pytest tests/integration/test_result_collector.py -v
pytest tests/integration/test_database_operations.py -v

# Commit and push IMMEDIATELY (Web model is waiting)
git add kosmos/execution/result_collector.py
git commit -m "Fix db_ops.create_result() call with required session and id (Bug #1)"
git push -u origin cli-critical-result-collector

# NOTIFY WEB MODEL: "result_collector Bug #1 complete, you can proceed with Bug #16"
```

### 2.2 World Model - WAIT FOR WEB

```bash
# WAIT: Web model must complete Bugs #5-6 first
# Monitor: git fetch origin && git log origin/web-critical-world-model

# After Web's fixes are merged:
git checkout main
git pull origin main
git checkout -b cli-critical-world-model

# Bug #2: Fix create_author()
# File: kosmos/world_model/simple.py (lines 193-199)
# Remove email and metadata parameters

# Bug #3: Fix create_method()
# File: kosmos/world_model/simple.py (lines 216-222)
# Remove extra parameter

# Bug #4: Fix create_citation()
# File: kosmos/world_model/simple.py (lines 446-451)
# Fix parameter name

# Test ALL world model methods:
pytest tests/integration/test_world_model.py -v
pytest tests/unit/world_model/test_simple.py -v

git add kosmos/world_model/simple.py
git commit -m "Fix world model method signatures: create_author, create_method, create_citation (Bugs #2-4)"
git push -u origin cli-critical-world-model
```

### 2.3 LLM Providers - WAIT FOR WEB

```bash
# WAIT: Web model must complete Bug #9 first
# Monitor: git fetch origin && git log origin/web-high-llm

# After Web's fix is merged:
git checkout main
git pull origin main
git checkout -b cli-high-llm

# Bugs #8-9: LLM Core Response Validation
# File: kosmos/core/llm.py (lines 321, 392)
# Add array bounds checking (Web already added type check)

# Test with mocked responses:
pytest tests/unit/core/test_llm.py -v
pytest tests/integration/test_llm_providers.py -v --mock-api

git add kosmos/core/llm.py
git commit -m "Add LLM response array bounds checking (Bugs #8-9)"
git push -u origin cli-high-llm
```

### 2.4 Result Collector Type Checking - AFTER WEB

```bash
# WAIT: Web model must complete Bug #16 first
# This is your Bug #31

git checkout main
git pull origin main
git checkout -b cli-medium-result-collector

# Bug #31: Non-Numeric Data Type Checking
# File: kosmos/execution/result_collector.py (lines 280-288)
# Add type validation for numeric operations

# Test with various data types:
pytest tests/unit/execution/test_result_collector.py::test_numeric_operations -v
pytest tests/integration/test_result_types.py -v

git add kosmos/execution/result_collector.py
git commit -m "Add type checking for non-numeric data operations (Bug #31)"
git push -u origin cli-medium-result-collector
```

### 2.5 Run Command - Independent

```bash
# Bug #20: Research Plan Validation
# File: kosmos/cli/commands/run.py (lines 296-302)
# Add null check:
if research_plan is None:
    raise ValueError("Research plan not initialized")
if research_plan.hypothesis_pool is None:
    research_plan.hypothesis_pool = []

# Test: pytest tests/integration/test_run_command.py -v
# Commit: "Add research plan validation (Bug #20)"
```

## Testing Strategy

### After Each Fix:

```bash
# 1. Unit test the specific module
pytest tests/unit/[module]/ -v --tb=short

# 2. Check for regressions
pytest tests/ -v --lf  # Run last failed

# 3. Verify imports still work
python -c "from kosmos.[module] import *"

# 4. Type checking
mypy kosmos/[module]/ --ignore-missing-imports
```

### Integration Testing:

```bash
# After completing a category of fixes:

# Knowledge modules:
pytest tests/integration/test_knowledge_pipeline.py -v

# Literature modules:
pytest tests/integration/test_literature_search.py -v

# Execution pipeline:
pytest tests/integration/test_execution_pipeline.py -v

# Full suite:
pytest tests/ -v --tb=short
```

### Platform-Specific Testing:

```bash
# For Windows path handling (Bug #15):
# Test on WSL2 environment
docker run --rm -v $(pwd):/app python:3.11 pytest tests/integration/test_sandbox.py

# For async issues (Bug #29):
# Test with different event loop policies
python -m pytest tests/unit/agents/ -v --asyncio-mode=strict
```

## Merge Order Protocol

### Your Merge Sequence:

1. **cli-critical-result-collector** - MUST merge first (Web is waiting)
2. **Immediate merges** - All Phase 1 bugs (no conflicts)
3. **cli-critical-world-model** - ONLY after Web's world_model PR
4. **cli-high-llm** - ONLY after Web's LLM PR
5. **cli-medium-result-collector** - After Web's Bug #16

### Communication Checkpoints:

```markdown
## Checkpoint 1 (Immediate)
✅ Starting: result_collector Bug #1
🔔 Notify Web: "Starting critical result_collector fix"

## Checkpoint 2 (After Bug #1)
✅ Completed: result_collector Bug #1
⏳ Starting: Phase 1 non-conflicting bugs
🔔 Notify Web: "Bug #1 complete, you can proceed with Bug #16"

## Checkpoint 3 (Waiting)
✅ Completed: All Phase 1 bugs
⏳ Waiting: Web's world_model fixes
🔔 Notify Web: "Ready to apply world_model fixes after yours"

## Checkpoint 4 (Final)
✅ Completed: All 29 CLI bugs
🔔 Notify Web: "All CLI fixes complete, ready for integration"
```

## Priority Order

If time is limited, prioritize in this order:

1. **CRITICAL FIRST:** Bug #1 (result_collector - Web is blocked)
2. **TEST BASICS:** Bugs #5-7 (broken imports block testing)
3. **RUNTIME ERRORS:** Bugs #13-14 (NoneType crashes)
4. **API VALIDATION:** Bugs #16-18 (external API handling)
5. **AFTER WEB:** Bugs #2-4 (world_model), #8-12 (LLM)
6. **LOWER:** Test fixtures #22-28
7. **LOWEST:** Bug #31 (after Web's #16)

## Success Criteria

Your work is complete when:

1. ✅ All 29 bugs from CLI_BASED_BUGS.md are fixed
2. ✅ Each fix has passing tests
3. ✅ Integration tests pass: >90% pass rate (from 57.4% baseline)
4. ✅ Code coverage improved: >70% (from 22.77% baseline)
5. ✅ No merge conflicts with Web model's fixes
6. ✅ Full test suite passes: `pytest tests/ -v`

## Handling Test Failures

When a test fails after your fix:

```bash
# 1. Get detailed failure info
pytest [failing_test] -vvs --tb=long

# 2. Check if it's a cascading effect
pytest [failing_test] --pdb  # Drop into debugger

# 3. Verify your assumptions about the model
python -c "from kosmos.models import [Model]; print([Model].__fields__)"

# 4. Check for test isolation issues
pytest [failing_test] --forked  # Run in subprocess

# 5. If still failing, document in commit:
git commit -m "Partial fix for Bug #X - test Y still failing due to Z"
```

## Remember

- You're working in `../kosmos-cli-fixes/` directory
- Web model is in `../kosmos-web-fixes/` directory
- **Bug #1 is CRITICAL** - Web model needs this to proceed
- Test everything - these bugs were found through test failures
- Wait for Web's fixes on shared files before proceeding
- Communicate at checkpoints
- Full test suite should show significant improvement

Good luck! Start with Bug #1 immediately as Web model is waiting.