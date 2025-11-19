# Web Model Bug-Fixing Instructions - Kosmos AI Scientist v0.2.0

**Role:** Web-based Claude Code Model
**Task:** Fix 31 bugs from WEB_BASED_BUGS.md
**Working Directory:** `../kosmos-web-fixes/`
**Coordination:** You will work in parallel with a CLI model fixing different bugs

## CRITICAL: READ THIS FIRST

You are working alongside another AI model (CLI) that is fixing different bugs simultaneously. To prevent merge conflicts:

1. **YOU OWN THESE FILES EXCLUSIVELY** (no conflicts possible):
   - `kosmos/config.py` (Bug #1)
   - `pyproject.toml` (Bugs #2, #3, #31)
   - `pytest.ini` (Bug #8)
   - `kosmos/cli/interactive.py` (Bugs #27, #28)
   - `kosmos/safety/code_validator.py` (Bug #18)
   - `kosmos/safety/guardrails.py` (Bug #19)
   - `kosmos/domains/biology/genomics.py` (Bugs #11, #12)
   - `kosmos/domains/materials/apis.py` (Bug #20)
   - `kosmos/domains/neuroscience/neurodegeneration.py` (Bug #7)
   - `kosmos/analysis/summarizer.py` (Bugs #13, #14)
   - `kosmos/execution/code_generator.py` (Bug #15)
   - `kosmos/models/result.py` (Bug #10)
   - `kosmos/cli/commands/cache.py` (Bug #17)

2. **SHARED FILES REQUIRING COORDINATION**:
   - `kosmos/world_model/simple.py` - YOU MUST FIX FIRST (Bugs #5, #6)
   - `kosmos/core/llm.py` - YOU MUST FIX FIRST (Bug #9)
   - `kosmos/execution/result_collector.py` - WAIT FOR CLI's Bug #1 (then fix Bug #16)
   - `kosmos/cli/commands/run.py` - Can work independently (Bug #4)

## Setup Instructions

### Step 1: Create Git Worktree

```bash
# From the main Kosmos directory
cd /mnt/c/python/Kosmos
git fetch origin main

# Create your dedicated worktree
git worktree add ../kosmos-web-fixes --detach origin/main
cd ../kosmos-web-fixes

# Create your working branch
git checkout -b web-bugfix-$(date +%Y%m%d-%H%M%S)
git push -u origin HEAD
```

### Step 2: Verify Setup

```bash
# Confirm you're in the correct worktree
pwd  # Should show: /mnt/c/python/kosmos-web-fixes

# Confirm correct branch
git branch --show-current  # Should show: web-bugfix-[timestamp]

# Confirm clean state
git status  # Should show: nothing to commit, working tree clean
```

## Phase 1: Non-Conflicting Fixes (Do These First)

These can be done immediately without any coordination:

### 1.1 Critical Dependencies (Do First)

```bash
# Bug #1: Pydantic V2 Configuration
# File: kosmos/config.py
# Add BeforeValidator for comma-separated string parsing
# Test: python -c "from kosmos.config import KosmosSettings"

# Bug #2-3: Missing Dependencies
# File: pyproject.toml
# Add: psutil = "^5.9.0" and redis = "^5.0.0"
# Commit: "Add missing psutil and redis dependencies (Bugs #2, #3)"

# Bug #8: Missing pytest marker
# File: pytest.ini
# Add e2e marker to [tool.pytest.ini_options]
# Commit: "Add e2e marker to pytest configuration (Bug #8)"
```

### 1.2 Safety and Validation Modules

```bash
# Bug #18: False Positives in Code Validator
# File: kosmos/safety/code_validator.py (lines 245-251, 267-275)
# Replace string matching with AST parsing
# Commit: "Fix code validator false positives with AST parsing (Bug #18)"

# Bug #19: Falsy Value Bug
# File: kosmos/safety/guardrails.py (lines 156-170)
# Change: if limit: → if limit is not None:
# Commit: "Fix resource limit bypass for zero values (Bug #19)"
```

### 1.3 Domain-Specific Fixes

```bash
# Bug #11-12: Missing Biology API Methods
# File: kosmos/domains/biology/genomics.py
# Implement get_pqtl() and get_atac_peaks() methods
# Commit: "Add missing biology API methods (Bugs #11, #12)"

# Bug #20: PerovskiteDB Type Safety
# File: kosmos/domains/materials/apis.py (lines 682-685)
# Convert Series to dict: result.to_dict()
# Commit: "Fix PerovskiteDB pandas type handling (Bug #20)"

# Bug #7: scipy Import Error
# File: kosmos/domains/neuroscience/neurodegeneration.py (line 485)
# Replace: from scipy.stats import false_discovery_control
# With: from statsmodels.stats.multitest import multipletests
# Commit: "Fix scipy import to use statsmodels (Bug #7)"
```

### 1.4 Analysis and Models

```bash
# Bug #13-14: Missing Model Fields
# File: kosmos/analysis/summarizer.py
# Add is_primary field (line 189) and CI fields (line 280)
# Commit: "Add missing StatisticalTestResult and ExperimentResult fields (Bugs #13, #14)"

# Bug #10: Pydantic Validator Dict Access
# File: kosmos/models/result.py (lines 209-217)
# Change: values.test_name → values['test_name']
# Commit: "Fix Pydantic validator dict access (Bug #10)"

# Bug #15: Enum.lower() Method
# File: kosmos/execution/code_generator.py (lines 65, 139, 154)
# Change: test_type.lower() → test_type.value.lower()
# Commit: "Fix enum value access in code generator (Bug #15)"
```

### 1.5 CLI Components (Non-Conflicting)

```bash
# Bug #17: Cache Type Enum
# File: kosmos/cli/commands/cache.py (line 264)
# Change: "GENERAL" → CacheType.GENERAL
# Commit: "Fix cache type enum usage (Bug #17)"

# Bug #27-28: Interactive Mode
# File: kosmos/cli/interactive.py
# Fix type consistency (line 236) and add max_iterations validation
# Commit: "Fix interactive mode type handling and validation (Bugs #27, #28)"
```

### 1.6 Test Fixtures

```bash
# Bugs #21-26: Test Fixture Field Names
# Files: tests/integration/test_analysis_pipeline.py, tests/unit/agents/test_data_analyst.py
# Fix all field name mismatches as specified in WEB_BASED_BUGS.md
# Commit: "Fix test fixture field names and types (Bugs #21-26)"
```

### 1.7 General Improvements

```bash
# Bug #29: Hardcoded Paths
# Multiple files
# Replace "./data" with Path.cwd() / "data"
# Commit: "Replace hardcoded paths with configurable paths (Bug #29)"

# Bug #30: Deprecated datetime
# Multiple files
# Replace datetime.utcnow() with datetime.now(timezone.utc)
# Commit: "Replace deprecated datetime.utcnow() (Bug #30)"

# Bug #31: Lock File
# Run: poetry lock
# Commit: "Generate poetry.lock file (Bug #31)"
```

## Phase 2: Coordinated Fixes (CRITICAL TIMING)

### 2.1 World Model Fixes (YOU GO FIRST)

**IMPORTANT: The CLI model is waiting for you to complete these fixes first!**

```bash
# Create a separate branch for this critical fix
git checkout -b web-critical-world-model

# Bug #5: Fix create_paper() method
# File: kosmos/world_model/simple.py (lines 144-155)
# Fix parameter structure to match interface

# Bug #6: Fix create_concept() method
# File: kosmos/world_model/simple.py (lines 171-176)
# Remove extra metadata parameter

# Commit and push immediately
git add kosmos/world_model/simple.py
git commit -m "Fix world model method signatures: create_paper, create_concept (Bugs #5-6)"
git push -u origin web-critical-world-model

# NOTIFY CLI MODEL: Post in coordination channel that world_model fixes are ready
```

### 2.2 LLM Provider Fix (YOU GO FIRST)

```bash
# After world_model is merged, create new branch
git checkout main
git pull origin main
git checkout -b web-high-llm

# Bug #9: Provider Type Check
# File: kosmos/core/llm.py (lines 651-652)
# Ensure type validation for LLMProvider
# Fix: Pass instance not class reference

git add kosmos/core/llm.py
git commit -m "Add provider type validation in get_provider() (Bug #9)"
git push -u origin web-high-llm

# NOTIFY CLI MODEL: LLM type check is ready
```

### 2.3 Result Collector (WAIT FOR CLI)

```bash
# WAIT: CLI model must fix Bug #1 (database args) first
# Check: git fetch origin && git log origin/cli-critical-result-collector

# After CLI's fix is merged:
git checkout main
git pull origin main
git checkout -b web-high-result-collector

# Bug #16: Serialization Keys
# File: kosmos/execution/result_collector.py (line 365)
# Add missing keys to exclude_keys_list

git add kosmos/execution/result_collector.py
git commit -m "Fix statistical test result serialization exclude keys (Bug #16)"
git push -u origin web-high-result-collector
```

### 2.4 Run Command (Independent)

```bash
# Bug #4: Case Mismatch
# File: kosmos/cli/commands/run.py (lines 248-259)
# Fix: Use .lower() on enum comparison

git add kosmos/cli/commands/run.py
git commit -m "Fix workflow state string case mismatch (Bug #4)"
```

## Merge Order Protocol

### Your Merge Sequence:

1. **Immediate Merges** (Phase 1 bugs) - Can create PRs right away
2. **web-critical-world-model** - MUST be merged before CLI's world_model work
3. **web-high-llm** - MUST be merged before CLI's LLM work
4. **web-high-result-collector** - ONLY after CLI's result_collector Bug #1

### Communication Checkpoints:

```markdown
## Checkpoint 1 (After Phase 1)
✅ Completed: Config, dependencies, safety, domains, analysis
⏳ Starting: world_model fixes
🔔 Notify CLI: "Phase 1 complete, starting world_model"

## Checkpoint 2 (After world_model)
✅ Completed: world_model bugs #5-6
⏳ Starting: LLM provider fix
🔔 Notify CLI: "world_model PR ready for review"

## Checkpoint 3 (After LLM)
✅ Completed: LLM bug #9
⏳ Waiting: CLI's result_collector #1
🔔 Notify CLI: "LLM PR ready, waiting for result_collector"

## Checkpoint 4 (Final)
✅ Completed: All 31 web bugs
🔔 Notify CLI: "All web fixes complete, ready for integration"
```

## Testing After Each Fix

```bash
# After each commit, run basic validation:
python -m py_compile [modified_file.py]
mypy [modified_file.py] --ignore-missing-imports

# After completing a module:
pytest tests/unit/[module_name]/ -v --tb=short

# Before creating PR:
pytest tests/ -v -k "not integration" --tb=short
```

## Handling Conflicts (If They Occur)

If you encounter a merge conflict:

```bash
# 1. Don't panic - fetch latest
git fetch origin main

# 2. See what changed
git diff origin/main..HEAD -- [conflicted_file]

# 3. If conflict in world_model/simple.py:
#    - Your changes: lines 144-176 (create_paper, create_concept)
#    - CLI changes: lines 193-451 (create_author, create_method, create_citation)
#    - Resolution: Keep both (non-overlapping methods)

# 4. If conflict in llm.py:
#    - Your changes: lines 651-652 (type check)
#    - CLI changes: lines 321, 392 (array bounds)
#    - Resolution: Keep both (different sections)

# 5. After resolution:
git add [resolved_file]
git commit -m "Merge: Resolved conflict in [file]"
git push
```

## Success Criteria

Your work is complete when:

1. ✅ All 31 bugs from WEB_BASED_BUGS.md are fixed
2. ✅ Each fix has its own commit with descriptive message
3. ✅ No test regressions (existing tests still pass)
4. ✅ Type checking passes: `mypy kosmos/ --ignore-missing-imports`
5. ✅ Linting passes: `ruff check kosmos/`
6. ✅ CLI model confirms no conflicts with their fixes

## Priority Order

If time is limited, prioritize in this order:

1. **MUST DO FIRST:** Bugs #1, #2, #3 (blocks everything else)
2. **CRITICAL COORDINATION:** Bugs #5, #6 (world_model - CLI is waiting)
3. **HIGH PRIORITY:** Bug #9 (LLM - CLI needs this)
4. **MEDIUM:** All other Phase 1 bugs (no conflicts)
5. **LOWER:** Bug #16 (after CLI fixes database)
6. **LOWEST:** Test fixtures (Bugs #21-26)

## Remember

- You're working in `../kosmos-web-fixes/` directory
- CLI model is in `../kosmos-cli-fixes/` directory
- Communicate at checkpoints
- Test after each fix
- Follow the merge order strictly for shared files
- Your world_model and LLM fixes MUST happen before CLI's

Good luck! Start with Phase 1 bugs while coordinating on Phase 2 timing.