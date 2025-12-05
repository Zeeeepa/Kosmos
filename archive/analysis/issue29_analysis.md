# Issue #29 Analysis Report

**Issue:** Database schema incomplete & `'NoneType' object has no attribute 'enable_cache'` when running kosmos
**Reporter:** sujunhao
**Reported:** November 27, 2025
**Status:** OPEN
**Version:** Kosmos v0.2.0

---

## Executive Summary

Issue #29 reports two interconnected problems encountered when running Kosmos with an OpenAI-compatible provider (Ollama):

1. **Missing Database Indexes** - After running `alembic upgrade head`, `kosmos doctor` reports missing indexes despite migrations being at head revision
2. **Runtime Crash** - Executing `kosmos run --interactive` fails with `'NoneType' object has no attribute 'enable_cache'`

This analysis identifies **2 distinct root causes** and provides detailed fix recommendations.

---

## Problem 1: Missing Database Indexes

### Symptom

```
Missing indexes: hypotheses.ix_hypotheses_domain_status, experiments.ix_experiments_domain_status,
experiments.ix_experiments_created_at, results.ix_results_experiment_id, papers.ix_papers_domain_relevance
```

### Root Cause: Index Naming Prefix Mismatch

The validation code in `kosmos/utils/setup.py` expects indexes with the `ix_` prefix, but the migration creates indexes with the `idx_` prefix.

**Validation expects (lines 168-172):**
```python
expected_indexes = {
    "hypotheses": ["ix_hypotheses_domain_status"],
    "experiments": ["ix_experiments_created_at", "ix_experiments_domain_status"],
    "results": ["ix_results_experiment_id"],
    "papers": ["ix_papers_domain_relevance"]
}
```

**Migration creates (`alembic/versions/fb9e61f33cbf_add_performance_indexes.py`):**
```python
op.create_index('idx_hypotheses_domain_status', ...)  # Note: idx_ not ix_
op.create_index('idx_experiments_domain_status', ...)
op.create_index('idx_experiments_created_at', ...)
op.create_index('idx_results_experiment_id', ...)
op.create_index('idx_papers_domain_relevance', ...)
```

### Impact

- **Severity:** Low (cosmetic/diagnostic)
- **Functional Impact:** None - indexes exist and work correctly with `idx_` prefix
- **User Experience:** Confusing false-positive error messages during `kosmos doctor`

### Affected Files

| File | Line(s) | Issue |
|------|---------|-------|
| `kosmos/utils/setup.py` | 168-172 | Expects `ix_` prefix for index names |
| `alembic/versions/fb9e61f33cbf_add_performance_indexes.py` | All index definitions | Creates indexes with `idx_` prefix |

### Recommended Fix

**Option A: Update validation to match migration (Recommended)**

Update `kosmos/utils/setup.py` lines 168-172:

```python
# Change from ix_ to idx_ prefix
expected_indexes = {
    "hypotheses": ["idx_hypotheses_domain_status"],
    "experiments": ["idx_experiments_created_at", "idx_experiments_domain_status"],
    "results": ["idx_results_experiment_id"],
    "papers": ["idx_papers_domain_relevance"]
}
```

**Option B: Update migration to match validation**

This would require a new migration to rename all indexes from `idx_*` to `ix_*`, which is more invasive.

---

## Problem 2: `'NoneType' object has no attribute 'enable_cache'`

### Symptom

When running `kosmos run --interactive` with an OpenAI-compatible provider (Ollama), the application crashes with:
```
✗ Research failed: 'NoneType' object has no attribute 'enable_cache'
```

### Root Cause: Missing Null Check After Issue #22 Fix

The fix for Issue #22 made the `claude` configuration field optional (returning `None` when `ANTHROPIC_API_KEY` is not set). However, several code paths still access `config.claude.enable_cache` without checking if `config.claude` is `None`.

**Issue #22 fix in `kosmos/config.py` (line 868):**
```python
claude: Optional[ClaudeConfig] = Field(default_factory=_optional_claude_config)
```

**Factory function (lines 822-827):**
```python
def _optional_claude_config() -> Optional[ClaudeConfig]:
    """Create ClaudeConfig only if ANTHROPIC_API_KEY is set."""
    import os
    if os.getenv("ANTHROPIC_API_KEY"):
        return ClaudeConfig()
    return None  # Returns None when using OpenAI/LiteLLM providers
```

**Problematic code in `kosmos/cli/commands/run.py`:**

```python
# Line 119 - Direct attribute access on potentially None object
config_obj.claude.enable_cache = not no_cache

# Line 141 - Direct attribute access in dict construction
flat_config = {
    ...
    "enable_cache": config_obj.claude.enable_cache,
}
```

### Impact

- **Severity:** Critical (blocks execution)
- **Functional Impact:** Users cannot run research with OpenAI or LiteLLM providers
- **Affected Operations:** `kosmos run`, `kosmos run --interactive`

### Execution Flow Leading to Crash

```
1. User configures LLM_PROVIDER=openai (or litellm)
2. User does NOT set ANTHROPIC_API_KEY (not needed for OpenAI/LiteLLM)
3. _optional_claude_config() returns None
4. KosmosConfig.claude = None
5. User runs: kosmos run --interactive
6. run_research() calls get_config()
7. Code accesses config_obj.claude.enable_cache (line 119 or 141)
8. AttributeError: 'NoneType' object has no attribute 'enable_cache'
```

### Affected Files

| File | Line(s) | Issue |
|------|---------|-------|
| `kosmos/cli/commands/run.py` | 119 | `config_obj.claude.enable_cache = not no_cache` - No null check |
| `kosmos/cli/commands/run.py` | 141 | `"enable_cache": config_obj.claude.enable_cache` - No null check |

### Files with Proper Null Checks (for reference)

These files correctly handle the optional `claude` field:

| File | Line(s) | Pattern Used |
|------|---------|--------------|
| `kosmos/cli/main.py` | 179, 184 | `if config.claude:` guard |
| `kosmos/cli/commands/config.py` | 128, 231 | `if config.claude:` guard |
| `kosmos/knowledge/concept_extractor.py` | 126 | `config.claude.api_key if config.claude else None` |
| `kosmos/core/providers/factory.py` | 108 | `hasattr(kosmos_config, 'claude') and kosmos_config.claude` |

### Recommended Fix

**Fix for `kosmos/cli/commands/run.py`:**

**Current code (lines 119-141):**
```python
config_obj.claude.enable_cache = not no_cache

# Create flattened config dict for agents
flat_config = {
    ...
    "enable_cache": config_obj.claude.enable_cache,
}
```

**Proposed fix:**
```python
# Handle cache setting for different providers
if config_obj.claude:
    config_obj.claude.enable_cache = not no_cache
    cache_enabled = config_obj.claude.enable_cache
elif config_obj.litellm:
    # LiteLLM doesn't have a per-config cache setting
    cache_enabled = not no_cache
else:
    # OpenAI or other providers
    cache_enabled = not no_cache

# Create flattened config dict for agents
flat_config = {
    ...
    "enable_cache": cache_enabled,
}
```

**Alternative simpler fix:**
```python
# Determine cache setting based on available config
cache_enabled = not no_cache

# Apply to Claude config if present
if config_obj.claude:
    config_obj.claude.enable_cache = cache_enabled

# Create flattened config dict for agents
flat_config = {
    ...
    "enable_cache": cache_enabled,
}
```

---

## Related Issues

### Issue #22: ANTHROPIC_API_KEY Required Even with OpenAI Provider

- **Status:** Fixed (commit de0b28e)
- **Relationship:** Issue #29's `enable_cache` error is a **direct consequence** of the fix for Issue #22
- **Problem:** The fix made `claude` optional but didn't update all code paths that access `config.claude.*`

### Issue #6: Kosmos Stalls with Ollama

- **Status:** Fixed (commit dfcdea2)
- **Relationship:** Same user profile (OpenAI-compatible local models)
- **Problem:** JSON parsing and retry logic issues with local models

---

## Summary of Required Changes

### Priority 1: Critical (Blocks Execution)

| File | Change Required | Priority |
|------|-----------------|----------|
| `kosmos/cli/commands/run.py` | Add null check for `config_obj.claude` at lines 119 and 141 | **Critical** |

### Priority 2: Low (Cosmetic)

| File | Change Required | Priority |
|------|-----------------|----------|
| `kosmos/utils/setup.py` | Change `ix_` to `idx_` in expected index names (lines 168-172) | Low |

---

## Testing Strategy

### Unit Tests Required

1. **Configuration with OpenAI provider only:**
   ```python
   def test_run_command_with_openai_provider():
       """Verify run command works without ANTHROPIC_API_KEY."""
       with patch.dict(os.environ, {
           'LLM_PROVIDER': 'openai',
           'OPENAI_API_KEY': 'sk-test',
           'OPENAI_MODEL': 'gpt-4'
       }, clear=True):
           config = get_config(reload=True)
           assert config.claude is None
           # run_research should not crash
   ```

2. **Index validation with correct naming:**
   ```python
   def test_validate_database_schema_index_names():
       """Verify index validation uses correct naming convention."""
       # After fix, validation should pass when indexes exist with idx_ prefix
   ```

### Integration Tests

1. **End-to-end with Ollama:**
   ```bash
   export LLM_PROVIDER=litellm
   export LITELLM_MODEL=ollama/llama3.1:8b
   export LITELLM_API_BASE=http://localhost:11434
   # No ANTHROPIC_API_KEY needed
   kosmos run --interactive
   ```

### Manual Verification

```bash
# 1. Verify doctor passes after index fix
kosmos doctor

# 2. Verify interactive mode works with OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=ollama
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_MODEL=llama3.1:8b
kosmos run --interactive
```

---

## Conclusion

Issue #29 consists of two separate bugs:

1. **Index naming mismatch** - A simple cosmetic bug where validation expects `ix_` prefix but migration creates `idx_` prefix. The indexes exist and work correctly; only the doctor diagnostic is affected.

2. **NoneType enable_cache error** - A regression introduced by the fix for Issue #22. When the `claude` field was made optional to support non-Anthropic providers, several code paths in `run.py` were not updated to handle the case where `config.claude` is `None`.

**Estimated Fix Complexity:**
- Index naming: ~5 minutes (1 file, 4 line changes)
- Enable_cache null check: ~15 minutes (1 file, ~10 line changes)

**Testing Required:**
- Unit tests: ~30 minutes
- Integration tests: ~15 minutes

---

*Report generated: 2025-11-27*
*Analyzed by: Claude Code Analysis*
*Related Issues: #6 (Ollama stalling - fixed), #22 (ANTHROPIC_API_KEY requirement - fixed)*
