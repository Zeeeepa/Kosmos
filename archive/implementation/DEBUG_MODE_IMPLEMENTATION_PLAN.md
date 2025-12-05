# Debug Mode Implementation Plan for Kosmos AI Scientist

*Analysis Date: 2025-11-29*
*Prepared by: Claude Code Analysis*

---

## 1. Executive Summary

Kosmos has a solid logging foundation with JSON/text formatters, rotating file handlers, and existing CLI flags (`--verbose`, `--debug`). However, only **123 debug-level log statements** exist across **40 files** (of 93 files with logging), leaving critical execution paths under-instrumented. The most significant gap is in the research loop's decision-making and multi-step orchestration, making it difficult to diagnose issues like those reported in Issue #34 (research timeout). This plan proposes a tiered debug system with minimal overhead when disabled, comprehensive stage tracking for real-time observability, and structured error capture at all failure points.

---

## 2. Configuration Design

### 2.1 Recommended Configuration Schema

**Location**: Extend `kosmos/config.py` (existing `LoggingConfig` class)

```python
class LoggingConfig(BaseSettings):
    # Existing fields
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["json", "text"] = "json"
    file: Optional[str] = "logs/kosmos.log"
    debug_mode: bool = False

    # NEW: Granular debug controls
    debug_level: Literal[0, 1, 2, 3] = Field(
        default=0,
        description="Debug verbosity: 0=off, 1=critical path, 2=full trace, 3=data dumps",
        alias="DEBUG_LEVEL"
    )

    debug_modules: Optional[List[str]] = Field(
        default=None,
        description="Modules to debug (None=all when debug_mode=True)",
        alias="DEBUG_MODULES"
    )

    log_llm_calls: bool = Field(
        default=False,
        description="Log LLM request/response summaries",
        alias="LOG_LLM_CALLS"
    )

    log_agent_messages: bool = Field(
        default=False,
        description="Log inter-agent message routing",
        alias="LOG_AGENT_MESSAGES"
    )

    log_workflow_transitions: bool = Field(
        default=False,
        description="Log state machine transitions with timing",
        alias="LOG_WORKFLOW_TRANSITIONS"
    )

    stage_tracking_enabled: bool = Field(
        default=False,
        description="Enable real-time stage tracking output",
        alias="STAGE_TRACKING_ENABLED"
    )

    stage_tracking_output: Literal["stdout", "file", "jsonl"] = Field(
        default="jsonl",
        description="Stage tracking output format",
        alias="STAGE_TRACKING_OUTPUT"
    )

    stage_tracking_file: str = Field(
        default="logs/stages.jsonl",
        description="Stage tracking output file",
        alias="STAGE_TRACKING_FILE"
    )
```

### 2.2 CLI Flag Extensions

**Location**: `kosmos/cli/main.py:69-75`

```python
@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
    trace: bool = typer.Option(False, "--trace", help="Enable trace-level logging (very verbose)"),
    debug_level: int = typer.Option(0, "--debug-level", help="Debug level 0-3"),
    debug_modules: str = typer.Option(None, "--debug-modules", help="Comma-separated modules to debug"),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
):
```

### 2.3 Runtime Toggle Capability

**Requirement**: Enable debug without restart via:
1. Signal handler (SIGUSR1) to toggle debug level
2. Expose `/api/debug` endpoint for dynamic reconfiguration
3. Watch file `~/.kosmos/debug.json` for config changes

---

## 3. Instrumentation Map

### 3.1 Critical Path Instrumentation (Priority 1)

| Module/File | Function/Method | What to Log | Log Level | Rationale |
|-------------|-----------------|-------------|-----------|-----------|
| `agents/research_director.py:1200` | `decide_next_action()` | Decision inputs, evaluated state, chosen action | DEBUG | Phase transition decisions are invisible |
| `agents/research_director.py:1266` | `_execute_next_action()` | Action type, target agent, dispatch time | DEBUG | No visibility into action execution |
| `agents/research_director.py:1447` | `_should_check_convergence()` | Iteration count, hypothesis counts, convergence criteria | DEBUG | Hard to diagnose why convergence triggered |
| `cli/commands/run.py:247` | Research loop iteration | Iteration #, elapsed time, workflow state, counts | INFO | Loop progress completely opaque |
| `core/workflow.py:260` | `transition_to()` | From state, to state, action, duration in previous state | DEBUG | State transitions lack timing |

### 3.2 LLM Call Instrumentation (Priority 2)

| Module/File | Function/Method | What to Log | Log Level | Rationale |
|-------------|-----------------|-------------|-----------|-----------|
| `core/providers/anthropic.py:230` | `generate()` (before API call) | Model, prompt length, temperature | DEBUG | No visibility into what's being sent |
| `core/providers/anthropic.py:238` | `generate()` (after API call) | Tokens (in/out), latency_ms, finish_reason | DEBUG | Token usage hidden |
| `core/providers/anthropic.py:287` | Exception handler | Error type, HTTP status, raw error | ERROR | Errors lack context |
| `core/providers/openai.py:*` | All `generate*` methods | Same as anthropic | DEBUG | Same gaps in OpenAI provider |
| `core/providers/litellm_provider.py:*` | All `generate*` methods | Same as anthropic | DEBUG | Same gaps in LiteLLM provider |
| `core/llm.py:306` | API call | Model selected, input_tokens, output_tokens, latency | DEBUG | Per-call details |

### 3.3 Agent Communication (Priority 3)

| Module/File | Function/Method | What to Log | Log Level | Rationale |
|-------------|-----------------|-------------|-----------|-----------|
| `agents/base.py:235` | `send_message()` | From, to, message_type, correlation_id, content_preview | DEBUG | Message routing invisible |
| `agents/base.py:269` | `receive_message()` | From, type, processing time | DEBUG | Message processing not tracked |
| `agents/base.py:148` | `start()` | Agent type, agent_id, config summary | INFO | Agent lifecycle events |
| `agents/base.py:166` | `stop()` | Agent ID, reason, stats summary | INFO | Agent shutdown |

### 3.4 Execution Layer (Priority 3)

| Module/File | Function/Method | What to Log | Log Level | Rationale |
|-------------|-----------------|-------------|-----------|-----------|
| `execution/executor.py:148` | `execute()` | Code length, attempt #, retry status | DEBUG | Execution attempts hidden |
| `execution/executor.py:182` | `_execute_once()` | Execution time, stdout length, stderr length | DEBUG | Execution details |
| `execution/parallel.py:154` | `execute_batch()` | Task count, worker count, start time | INFO | Batch execution start |
| `execution/parallel.py:212` | `execute_batch()` completion | Completed, failed, total time, avg time | INFO | Batch summary |
| `orchestration/delegation.py:126` | `execute_plan()` | Task count, cycle #, context summary | INFO | Plan execution start |

---

## 4. Error Capture Analysis

### 4.1 Locations Requiring Enhanced Error Capture

| File:Line | Current Pattern | Issue | Recommended Fix |
|-----------|-----------------|-------|-----------------|
| `agents/research_director.py:104-107` | `except RuntimeError: pass` | DB init failure silently swallowed | Log warning with error details |
| `hypothesis/refiner.py:233,396,491,616,733` | `except Exception as e:` broad catch | Errors logged but context missing | Add stack trace, input parameters |
| `monitoring/alerts.py:280,302,312,328` | Bare `except:` | Swallows all exceptions including KeyboardInterrupt | Catch `Exception`, log with `exc_info=True` |
| `core/providers/factory.py:74` | `except Exception as e:` | Provider init failure loses raw error | Include raw error and config (redacted) |
| `orchestration/delegation.py:*` | Multiple exception handlers | Task failures not aggregated | Add task ID, retry count, cumulative errors |

### 4.2 Recommended Error Output Format

```python
@dataclass
class DebugError:
    timestamp: datetime
    error_type: str
    error_message: str
    module: str
    function: str
    line: int
    stack_trace: Optional[str]
    context: Dict[str, Any]  # Input params, state at time of error
    recoverable: bool
    recovery_action: Optional[str]  # What the code did in response

    def to_json(self) -> str:
        # Sanitize sensitive data before serialization
        return json.dumps(asdict(self), default=str)
```

### 4.3 Error Capture Decorator

```python
def capture_debug_error(func):
    """Decorator to capture and log errors with full context."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if config.logging.debug_mode:
                error_context = {
                    'args': repr(args)[:500],  # Truncate
                    'kwargs': {k: repr(v)[:100] for k, v in kwargs.items()},
                    'locals': {k: repr(v)[:100] for k, v in locals().items() if not k.startswith('_')}
                }
                logger.debug(
                    f"[ERROR] {func.__module__}.{func.__name__}: {e}",
                    extra={'context': error_context, 'exc_info': True}
                )
            raise
    return wrapper
```

---

## 5. Real-Time Observability Design

### 5.1 Stage Tracking System

**New File**: `kosmos/core/stage_tracker.py`

```python
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Literal
from contextlib import contextmanager
from datetime import datetime
import time
import json

@dataclass
class StageEvent:
    timestamp: str  # ISO format
    process_id: str  # Research run ID
    stage: str  # e.g., "GENERATE_HYPOTHESIS", "EXECUTE_EXPERIMENT"
    substage: Optional[str]  # e.g., "LLM_CALL", "DB_WRITE"
    status: Literal["started", "completed", "failed", "skipped"]
    duration_ms: Optional[int]
    iteration: int
    parent_stage: Optional[str]  # For nested stages
    output_summary: Optional[str]  # Truncated result summary
    error: Optional[Dict[str, str]]  # {type, message, recoverable}
    metadata: Dict[str, Any]  # Custom per-stage data

class StageTracker:
    """Context manager for tracking stage execution."""

    def __init__(self,
                 process_id: str,
                 output: Literal["stdout", "file", "jsonl"] = "jsonl",
                 output_file: str = "logs/stages.jsonl"):
        self.process_id = process_id
        self.output = output
        self.output_file = output_file
        self.file_handle = None
        self._stage_stack = []  # For nested stages
        self.current_iteration = 0

    def set_iteration(self, iteration: int):
        """Update current iteration number."""
        self.current_iteration = iteration

    @contextmanager
    def track(self, stage: str, **metadata):
        """Track a stage with timing and status."""
        start = time.time()
        event = StageEvent(
            timestamp=datetime.utcnow().isoformat(),
            process_id=self.process_id,
            stage=stage,
            substage=None,
            status="started",
            duration_ms=None,
            iteration=self.current_iteration,
            parent_stage=self._stage_stack[-1] if self._stage_stack else None,
            output_summary=None,
            error=None,
            metadata=metadata
        )
        self._emit(event)
        self._stage_stack.append(stage)

        try:
            yield event
            event.status = "completed"
            event.duration_ms = int((time.time() - start) * 1000)
        except Exception as e:
            event.status = "failed"
            event.duration_ms = int((time.time() - start) * 1000)
            event.error = {"type": type(e).__name__, "message": str(e)[:500]}
            raise
        finally:
            self._stage_stack.pop()
            self._emit(event)

    def _emit(self, event: StageEvent):
        """Emit stage event to configured output."""
        event_json = json.dumps(asdict(event), default=str)

        if self.output == "stdout":
            print(f"[STAGE] {event_json}")
        elif self.output in ("file", "jsonl"):
            with open(self.output_file, "a") as f:
                f.write(event_json + "\n")
```

### 5.2 Output Mechanisms Comparison

| Mechanism | Pros | Cons | Recommended Use |
|-----------|------|------|-----------------|
| JSONL file | Queryable, persistent, tailable | Requires file I/O | Primary output for production |
| stdout | Immediate, visible | Floods terminal, not queryable | Optional `--trace` flag for dev |
| Unix socket | Real-time, low overhead | Platform-specific | Future dashboard integration |
| SQLite | Highly queryable | More complex setup | Consider for full observability |

**Recommendation**: JSONL file as primary + optional stdout for development.

### 5.3 Standard Progress Event Format

```json
{
  "timestamp": "2025-11-29T14:23:45.123Z",
  "process_id": "research_abc123",
  "stage": "EXECUTE_EXPERIMENT",
  "substage": "RUN_CODE",
  "status": "completed",
  "duration_ms": 2345,
  "iteration": 3,
  "parent_stage": "DESIGN_EXPERIMENT",
  "output_summary": "Generated 5 results, p-value=0.023",
  "error": null,
  "metadata": {
    "hypothesis_id": "hyp_001",
    "protocol_id": "proto_001",
    "tokens_used": 1234
  }
}
```

---

## 6. Implementation Touchpoints

### 6.1 Configuration Changes

```
- file: kosmos/config.py
  changes: Add debug_level, debug_modules, log_llm_calls, log_agent_messages,
           log_workflow_transitions, stage_tracking_* fields to LoggingConfig

- file: kosmos/cli/main.py
  changes: Add --trace, --debug-level, --debug-modules CLI options (lines 69-75)
```

### 6.2 Instrumentation Additions

```
## Critical Path (Tier 1)
- file: kosmos/agents/research_director.py
  locations: lines 1200-1265, 1266-1446, 1447-1475, 442, 460-737
  type: Decision logging, action dispatch logging, convergence criteria logging

- file: kosmos/cli/commands/run.py
  locations: lines 247-314 (research loop)
  type: Iteration progress, phase timing, state tracking

- file: kosmos/core/workflow.py
  locations: lines 260-304 (transition_to method)
  type: State transition with timing

## LLM Calls (Tier 1)
- file: kosmos/core/providers/anthropic.py
  locations: lines 150-288 (generate method)
  type: Request/response logging with token counts

- file: kosmos/core/providers/openai.py
  locations: lines 100-250 (generate methods)
  type: Request/response logging

- file: kosmos/core/providers/litellm_provider.py
  locations: lines 120-300 (generate methods)
  type: Request/response logging

## Agent Communication (Tier 2)
- file: kosmos/agents/base.py
  locations: lines 148-195, 235-316
  type: Lifecycle events, message routing

## Execution Layer (Tier 2)
- file: kosmos/execution/executor.py
  locations: lines 125-180, 182-267
  type: Execution attempts, results

- file: kosmos/execution/parallel.py
  locations: lines 121-218
  type: Batch execution progress

- file: kosmos/orchestration/delegation.py
  locations: lines 126-220
  type: Plan execution, task routing
```

### 6.3 New Files Required

```
- file: kosmos/core/stage_tracker.py
  purpose: Real-time stage tracking with context managers

- file: kosmos/core/debug_utils.py
  purpose: Decorators (capture_debug_error), lazy evaluation helpers,
           data sanitization utilities

- file: kosmos/monitoring/debug_dashboard.py (optional, Tier 2)
  purpose: Optional web-based debug dashboard viewer
```

---

## 7. Tiered Implementation Plan

### Tier 1 - Minimal Viable Debug Mode

**Scope**: Single config flag, critical failure points, basic stage logging

**Changes**:
1. Extend `LoggingConfig` with `debug_level` (0-3)
2. Add CLI `--trace` flag for maximum verbosity
3. Add 15-20 strategic debug logs:
   - `research_director.py`: `decide_next_action()`, `_execute_next_action()`, phase transitions
   - `run.py`: Per-iteration summary with timing
   - `providers/*.py`: LLM call entry/exit with token counts
4. Create basic `StageTracker` with JSONL output
5. Add error context to top 10 exception handlers

**Estimated Touch Points**: 8 files
**Estimated Effort**: Low (1-2 days)

### Tier 2 - Full Observability

**Scope**: Granular config, comprehensive instrumentation, real-time streaming

**Changes**:
1. Add per-module debug toggles (`log_llm_calls`, `log_agent_messages`, etc.)
2. Instrument all 40+ files with logging:
   - Add debug logs to all agent methods
   - Add timing to all workflow transitions
   - Add message tracing to all inter-agent communication
3. Create `capture_debug_error` decorator and apply to critical functions
4. Add real-time stage streaming with Unix socket option
5. Create optional web dashboard for stage visualization
6. Add structured error reporting with context capture

**Estimated Touch Points**: 45+ files
**Estimated Effort**: Medium-High (1-2 weeks)

---

## 8. Warnings and Caveats

### 8.1 Performance Anti-Patterns to Avoid

| Location | Risk | Mitigation |
|----------|------|------------|
| `research_director.py` (hot path) | Excessive string formatting | Use lazy evaluation: `logger.debug("x=%s", x)` not `logger.debug(f"x={x}")` |
| `providers/*.py` | Logging large prompts/responses | Truncate to first/last 500 chars, log full only at TRACE level |
| `parallel.py` | Logging inside tight loops | Gate with `if logger.isEnabledFor(logging.DEBUG)` |
| All files | Creating debug objects when disabled | Use `@lazy_debug` decorator pattern |

### 8.2 Sensitive Data Redaction Required

| Location | Data Type | Action |
|----------|-----------|--------|
| `config.py` | API keys | Never log; redact to `sk-ant-***XXXX` |
| `providers/*.py` | Full prompts | Truncate; hash for correlation |
| `db/operations.py` | User research questions | Log only if user opts in |
| `literature/*.py` | API credentials | Never log |

### 8.3 Potential Circular Import Issues

| File | Risk | Solution |
|------|------|----------|
| `core/logging.py` | Importing `config` creates cycle | Use late binding / lazy import |
| `core/stage_tracker.py` | If imports agents | Keep stage_tracker dependency-free |

### 8.4 Existing Logging Conflicts

| Pattern | Current Usage | Recommendation |
|---------|---------------|----------------|
| `logger.info()` in loops | 22 instances | Gate or convert to DEBUG |
| Duplicate start/stop logs | Agent lifecycle | Consolidate to single entry |
| Inconsistent log format | Some use f-strings, some % | Standardize on lazy `%s` format |

---

## 9. Implementation Priority Order

1. **Phase 1** (Immediate - Issue #34 fix):
   - Add iteration timing to `run.py:247-314`
   - Add phase transition logging to `research_director.py:1200-1275`
   - Add convergence criteria logging

2. **Phase 2** (Week 1):
   - Implement `StageTracker` with JSONL output
   - Add LLM call logging to all providers
   - Add CLI `--trace` flag

3. **Phase 3** (Week 2):
   - Add per-module debug toggles
   - Instrument agent communication
   - Add error context decorators

4. **Phase 4** (Future):
   - Real-time streaming dashboard
   - Runtime toggle via signals/API
   - Performance profiling integration

---

## 10. Appendix: Analysis Statistics

| Metric | Value |
|--------|-------|
| Total Python files analyzed | 93 |
| Files with any logging | 93 |
| Total logging statements | 1068 |
| DEBUG level statements | 123 |
| Files with DEBUG statements | 40 |
| Bare `except:` clauses found | 4 |
| Broad `except Exception:` clauses | 60+ |
| Agent files | 12 |
| Provider files | 5 |
| Execution files | 10 |
| Orchestration files | 4 |

---

*This document is a read-only analysis. No files were modified during its creation.*
