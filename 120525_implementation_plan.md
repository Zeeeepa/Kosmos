# Kosmos Implementation Plan

**Date**: December 5, 2025
**Reference**: 120525_implementation_gaps.md
**Scope**: Code quality fixes, debug mode completion, documentation updates

---

## Executive Summary

This plan addresses all remaining implementation gaps identified in the gap analysis:

| Category | Items | Effort |
|----------|-------|--------|
| Silent Exception Handlers | 6 locations | Low |
| Debug Mode Features | 2 features | Medium |
| Documentation | README + CONTRIBUTING.md | Low |

**Total Files**: 9 (7 source + 2 documentation)

---

## Phase 1: Silent Exception Handler Fixes

All silent `except Exception: pass` patterns need logging added for debuggability.

### 1.1 kosmos/core/providers/openai.py

**Location**: Line 183-184
**Context**: Config retrieval for `log_llm_calls` feature flag

**Current Code:**
```python
except Exception:
    pass
```

**Fixed Code:**
```python
except Exception as e:
    logger.debug("Failed to load LLM call logging config: %s", e)
```

---

### 1.2 kosmos/core/providers/litellm_provider.py

**Location**: Line 298-299
**Context**: Config retrieval for `log_llm_calls` feature flag (identical to openai.py)

**Current Code:**
```python
except Exception:
    pass
```

**Fixed Code:**
```python
except Exception as e:
    logger.debug("Failed to load LLM call logging config: %s", e)
```

---

### 1.3 kosmos/execution/sandbox.py (Container Cleanup)

**Location**: Line 310
**Context**: Docker container cleanup - force kill fallback

**Current Code:**
```python
try:
    container.stop(timeout=5)
except Exception:
    container.kill()
```

**Fixed Code:**
```python
try:
    container.stop(timeout=5)
except Exception as e:
    logger.warning("Graceful container stop failed, forcing kill: %s", e)
    container.kill()
```

**Note**: Uses WARNING level because force kill indicates a problem worth tracking.

---

### 1.4 kosmos/execution/sandbox.py (Profiler Cleanup)

**Location**: Line 249-250
**Context**: Profiler stop during error handling cleanup

**Current Code:**
```python
except Exception:
    pass
```

**Fixed Code:**
```python
except Exception as e:
    logger.debug("Failed to stop profiler during error cleanup: %s", e)
```

---

### 1.5 kosmos/cli/main.py (Verbose Mode)

**Location**: Lines 83-84
**Context**: Verbose mode flag setup during CLI initialization

**Current Code:**
```python
except Exception:
    pass  # Config may not be available yet
```

**Fixed Code:**
```python
except Exception as e:
    logger.debug("Verbose mode config not applied (config not ready): %s", e)
```

---

### 1.6 kosmos/cli/main.py (Debug Modules)

**Location**: Lines 140-141
**Context**: Debug modules list configuration

**Current Code:**
```python
except Exception:
    pass  # Config may not be available yet
```

**Fixed Code:**
```python
except Exception as e:
    logger.debug("Debug modules config not applied (config not ready): %s", e)
```

---

### 1.7 kosmos/execution/executor.py

**Location**: Lines 68-69
**Context**: Profile data serialization in `ExecutionResult.to_dict()`

**Current Code:**
```python
except Exception:
    result['profile_data'] = None
```

**Fixed Code:**
```python
except Exception as e:
    logger.debug("Failed to serialize profile data: %s", e)
    result['profile_data'] = None
```

---

## Phase 2: Debug Mode Feature Implementation

Two config flags are defined but not implemented. Both follow the same pattern used by `log_llm_calls`.

### 2.1 Agent Message Logging

**File**: `kosmos/agents/base.py`
**Config Flag**: `config.logging.log_agent_messages`
**Log Prefix**: `[MSG]`

#### Implementation in send_message()

**Location**: After `message = AgentMessage(...)` (around line 248)

**Add Code:**
```python
# Log agent message if enabled
try:
    from kosmos.config import get_config
    if get_config().logging.log_agent_messages:
        logger.debug(
            "[MSG] %s -> %s: type=%s, correlation_id=%s, content_preview=%.100s",
            self.agent_id,
            to_agent,
            message_type.value,
            correlation_id or message.id,
            str(content)[:100]
        )
except Exception:
    pass  # Config not available
```

#### Implementation in receive_message()

**Location**: After `self.message_queue.append(message)` (around line 275)

**Add Code:**
```python
# Log received message if enabled
try:
    from kosmos.config import get_config
    if get_config().logging.log_agent_messages:
        logger.debug(
            "[MSG] %s <- %s: type=%s, msg_id=%s",
            self.agent_id,
            message.from_agent,
            message.type.value,
            message.id
        )
except Exception:
    pass  # Config not available
```

#### Expected Output

```
[MSG] research_director -> hypothesis_generator: type=REQUEST, correlation_id=abc123, content_preview={"task": "generate"...
[MSG] hypothesis_generator <- research_director: type=REQUEST, msg_id=abc123
```

---

### 2.2 Workflow Transition Logging

**File**: `kosmos/core/workflow.py`
**Config Flag**: `config.logging.log_workflow_transitions`
**Log Prefix**: `[WORKFLOW]`

#### Implementation in transition_to()

**Location**: In `transition_to()` method, after calculating `time_in_state`

**Add Code:**
```python
# Log workflow transition if enabled
log_transitions = False
try:
    from kosmos.config import get_config
    log_transitions = get_config().logging.log_workflow_transitions
except Exception:
    pass

if log_transitions:
    logger.debug(
        "[WORKFLOW] Transition: %s -> %s (was in %s for %.2fs) action='%s'",
        self.current_state.value,
        target_state.value,
        self.current_state.value,
        time_in_state,
        action
    )
```

#### Expected Output

```
[WORKFLOW] Transition: HYPOTHESIZING -> DESIGNING (was in HYPOTHESIZING for 12.34s) action='hypothesis_complete'
[WORKFLOW] Transition: DESIGNING -> EXECUTING (was in DESIGNING for 5.67s) action='design_complete'
```

---

## Phase 3: README Updates

**File**: `/mnt/c/python/kosmos/README.md`

### 3.1 Add Implementation Status Section

**Location**: After "Project Status" section

```markdown
## Implementation Status

### Recent Fixes (December 2025)

| Category | Status | Details |
|----------|--------|---------|
| Code Quality | 100% | All silent exception handlers now log appropriately |
| Debug Mode | 100% | All config flags fully implemented |
| Test Coverage | 55% | 15 critical modules pending (see 120525_implementation_gaps.md) |

### Debug Features Complete

- `--trace` flag for maximum verbosity
- `log_llm_calls` - Token counts and latency for all providers
- `log_agent_messages` - Inter-agent message routing
- `log_workflow_transitions` - State machine transitions with timing
- Stage tracking with JSONL output
```

### 3.2 Update Debug Mode Guide

**Location**: In existing "Debug Mode Guide" section, add subsections

```markdown
### Agent Message Logging

Enable with `LOG_AGENT_MESSAGES=true` or `--trace`:

```
[MSG] research_director -> hypothesis_generator: type=REQUEST, correlation_id=abc123
[MSG] hypothesis_generator <- research_director: type=REQUEST, msg_id=abc123
```

Shows inter-agent communication including:
- Sender and receiver agent IDs
- Message type (REQUEST, RESPONSE, NOTIFICATION, ERROR)
- Correlation ID for request/response tracking
- Content preview (first 100 chars)

### Workflow Transition Logging

Enable with `LOG_WORKFLOW_TRANSITIONS=true` or `--trace`:

```
[WORKFLOW] Transition: HYPOTHESIZING -> DESIGNING (was in HYPOTHESIZING for 12.34s) action='hypothesis_complete'
```

Shows state machine transitions including:
- Previous and new state
- Time spent in previous state
- Action that triggered the transition
```

### 3.3 Add Test Coverage Section

**Location**: Before "Documentation" section

```markdown
## Test Coverage

Current test suite: 339 unit + 43 integration + 39 E2E tests

### Running Tests

```bash
# Run all passing tests
pytest tests/unit/compression/ tests/unit/orchestration/ tests/unit/validation/ -v

# Run quick smoke test
pytest tests/unit/orchestration/ tests/unit/workflow/ -v --tb=short

# Run with coverage
pytest --cov=kosmos --cov-report=html
```

### Known Gaps

See `120525_implementation_gaps.md` for detailed analysis of modules needing test coverage.

Priority modules needing tests:
- `agents/base.py` - BaseAgent foundation class
- `agents/registry.py` - AgentRegistry singleton
- `core/metrics.py` - MetricsCollector and budget tracking
- `core/providers/*.py` - LLM provider implementations
```

---

## Phase 4: Create CONTRIBUTING.md

**File**: `/mnt/c/python/kosmos/CONTRIBUTING.md` (new file)

```markdown
# Contributing to Kosmos

Thank you for your interest in contributing to Kosmos!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jimmc414/Kosmos.git
   cd Kosmos
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Verify setup:
   ```bash
   kosmos doctor
   ```

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use f-strings for string formatting (or %-style for logger calls)

### Logging

- Use module-level logger: `logger = logging.getLogger(__name__)`
- Never use bare `except:` - always specify exception type
- Always log exceptions before silent fallback:

  ```python
  except Exception as e:
      logger.debug("Context message: %s", e)
      # fallback behavior
  ```

### Exception Handling

- Catch specific exceptions when possible
- Log context before re-raising or falling back
- Use WARNING for recoverable issues that indicate problems
- Use DEBUG for expected fallbacks in optional features

### Debug Logging Patterns

When adding debug logging gated by config flags:

```python
# Check config flag
try:
    from kosmos.config import get_config
    if get_config().logging.log_feature_name:
        logger.debug("[PREFIX] Message: %s", value)
except Exception:
    pass  # Config not available
```

## Testing

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests (requires Docker)
pytest tests/e2e/ -v

# With coverage
pytest --cov=kosmos --cov-report=html
```

### Writing Tests

- Place unit tests in `tests/unit/<module>/test_<file>.py`
- Use pytest fixtures from `conftest.py`
- Mock external services (LLM, database, Docker)
- Follow AAA pattern: Arrange, Act, Assert

Example test structure:
```python
def test_feature_does_something(mock_llm_client):
    # Arrange
    agent = SomeAgent(client=mock_llm_client)

    # Act
    result = agent.do_something()

    # Assert
    assert result.status == "success"
```

## Pull Request Process

1. Create feature branch from `master`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes with tests

3. Run tests and ensure all pass:
   ```bash
   pytest tests/unit/ tests/integration/ -v
   ```

4. Update documentation if needed

5. Submit PR with clear description:
   - What the change does
   - Why it's needed
   - How to test it

## Debug Mode

When debugging issues, use trace mode for maximum visibility:

```bash
kosmos run --trace --objective "..." --max-iterations 2
```

This enables all debug logging including:
- `[LLM]` - LLM call details (model, tokens, latency)
- `[MSG]` - Agent message routing
- `[WORKFLOW]` - State machine transitions
- `[DECISION]` - Research director decisions
- `[ITER]` - Per-iteration summaries

## Code Review Checklist

Before submitting, ensure:
- [ ] No bare `except:` clauses
- [ ] All exceptions are logged before silent handling
- [ ] Type hints on all public functions
- [ ] Tests for new functionality
- [ ] Documentation updated if needed

## Questions?

Open an issue for questions or suggestions.
```

---

## File Summary

### Source Code Changes (7 files)

| File | Changes | Lines |
|------|---------|-------|
| `kosmos/core/providers/openai.py` | Add exception logging | 183-184 |
| `kosmos/core/providers/litellm_provider.py` | Add exception logging | 298-299 |
| `kosmos/execution/sandbox.py` | Add exception logging (2 locations) | 249-250, 310 |
| `kosmos/execution/executor.py` | Add exception logging | 68-69 |
| `kosmos/cli/main.py` | Add exception logging (2 locations) | 83-84, 140-141 |
| `kosmos/agents/base.py` | Add agent message logging | send_message(), receive_message() |
| `kosmos/core/workflow.py` | Add workflow transition logging | transition_to() |

### Documentation Changes (2 files)

| File | Changes |
|------|---------|
| `README.md` | Add Implementation Status, update Debug Mode Guide, add Test Coverage section |
| `CONTRIBUTING.md` | Create new file with contribution guidelines |

---

## Execution Order

1. **Phase 1.1-1.7**: Fix all 6 silent exception handlers (quick wins, ~15 min)
2. **Phase 2.1**: Implement agent message logging in `base.py` (~10 min)
3. **Phase 2.2**: Implement workflow transition logging in `workflow.py` (~10 min)
4. **Phase 3**: Update `README.md` with new sections (~15 min)
5. **Phase 4**: Create `CONTRIBUTING.md` (~5 min)
6. **Verification**: Test changes work correctly
7. **Commit**: Single commit with message "Complete implementation gaps from 120525 analysis"

---

## Verification Steps

After implementation:

```bash
# 1. Verify no syntax errors
python -c "from kosmos.agents.base import BaseAgent"
python -c "from kosmos.core.workflow import ResearchWorkflow"

# 2. Verify imports work
python -c "from kosmos.core.providers.openai import OpenAIProvider"
python -c "from kosmos.execution.sandbox import SandboxExecutor"

# 3. Run quick test
pytest tests/unit/workflow/ -v --tb=short

# 4. Test debug logging manually
kosmos run --trace --objective "Test objective" --max-iterations 1

# 5. Check for new log prefixes
grep -E "\[MSG\]|\[WORKFLOW\]" logs/kosmos.log
```

---

## Success Criteria

- [ ] All 6 silent exception handlers now log before fallback
- [ ] `LOG_AGENT_MESSAGES=true` produces `[MSG]` log entries
- [ ] `LOG_WORKFLOW_TRANSITIONS=true` produces `[WORKFLOW]` log entries
- [ ] `--trace` flag enables all debug logging
- [ ] README.md documents all debug features
- [ ] CONTRIBUTING.md exists with code standards
- [ ] All existing tests still pass

---

*Generated: December 5, 2025*
*Reference: 120525_implementation_gaps.md*
