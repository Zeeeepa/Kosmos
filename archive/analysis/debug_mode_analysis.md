# Debug Mode Analysis

## Current State Assessment

Kosmos has a solid logging infrastructure but sparse DEBUG-level usage, making it difficult to diagnose execution issues like those reported in Issue #34.

---

## Existing Infrastructure

### CLI Flags

| Flag | Effect |
|------|--------|
| `--verbose`, `-v` | Sets log level to INFO |
| `--debug` | Sets log level to DEBUG |
| `--quiet`, `-q` | Suppresses non-essential output |

**Location**: `kosmos/cli/main.py:49-65`

### Configuration

```python
# kosmos/config.py - LoggingConfig
log_level: str = "INFO"          # DEBUG, INFO, WARNING, ERROR, CRITICAL
log_format: str = "json"         # json or text
log_file: str = "logs/kosmos.log"
debug_mode: bool = False
log_api_requests: bool = False
```

**Environment Variables**:
- `LOG_LEVEL`
- `LOG_FORMAT`
- `LOG_FILE`
- `DEBUG_MODE`
- `LOG_API_REQUESTS`

### Logging Implementation

**File**: `kosmos/core/logging.py`

Features:
- JSONFormatter with structured fields (timestamp, level, module, function, line)
- TextFormatter with ANSI color codes
- RotatingFileHandler (10MB max, 5 backups)
- ExperimentLogger for specialized experiment tracking

---

## Gap Analysis

### Missing DEBUG Coverage

The following areas lack sufficient DEBUG-level logging:

#### 1. Research Director Execution (Critical)

**File**: `kosmos/agents/research_director.py`

Missing logs for:
- Phase transition decisions (why GENERATE_HYPOTHESIS vs DESIGN_EXPERIMENT)
- Agent message sends/receives with correlation IDs
- Pending request tracking and resolution timing
- Strategy selection rationale

**Recommended additions**:
```python
logger.debug(f"Phase transition: {old_state} -> {new_state}, reason: {reason}")
logger.debug(f"Message sent to {agent_id}, correlation_id={msg.id}")
logger.debug(f"Pending requests: {len(self.pending_requests)}")
```

#### 2. LLM Call Details (High Priority)

**Files**: `kosmos/core/providers/*.py`

Missing logs for:
- Token usage (input, output, cached)
- API latency per call
- Model selection decisions
- Retry attempts with reasons

**Recommended additions**:
```python
logger.debug(f"LLM call: model={model}, input_tokens={usage.input_tokens}, output_tokens={usage.output_tokens}")
logger.debug(f"LLM latency: {elapsed_ms}ms")
```

#### 3. Research Loop Progress (High Priority)

**File**: `kosmos/cli/commands/run.py`

Missing logs for:
- Iteration timing and duration
- Hypothesis/experiment counts per iteration
- Convergence criteria evaluation
- Progress percentage calculations

**Recommended additions**:
```python
logger.debug(f"Iteration {i}: hypotheses={len(hyps)}, experiments={len(exps)}, elapsed={elapsed}s")
logger.debug(f"Convergence check: novelty={novelty:.2f}, threshold={threshold}")
```

#### 4. Agent Communication (Medium Priority)

**File**: `kosmos/agents/base.py`

Missing logs for:
- Message routing decisions
- Queue depths and processing times
- Agent lifecycle events (init, start, stop)

#### 5. Workflow State Machine (Medium Priority)

**File**: `kosmos/core/workflow.py`

Missing logs for:
- State transitions with timestamps
- Guard condition evaluations
- Action execution timing

---

## Priority Implementation Order

### Phase 1: Critical Path Visibility

1. **Research Director phase logging** - Add DEBUG logs for:
   - `decide_next_action()` decisions
   - `_execute_next_action()` dispatches
   - Concurrent operation timeouts/fallbacks

2. **Iteration progress logging** - Add to `run.py`:
   - Per-iteration summary
   - Phase timing breakdowns

### Phase 2: LLM Call Transparency

3. **Provider call logging** - Add to all providers:
   - Request/response summaries
   - Token counts and costs
   - Latency measurements

### Phase 3: Deep Debugging

4. **Agent coordination** - Add message tracing
5. **Workflow state machine** - Add transition logging

---

## Proposed `--trace` Flag

Add a `--trace` flag for maximum verbosity:

```python
# kosmos/cli/main.py
@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    debug: bool = typer.Option(False, "--debug"),
    trace: bool = typer.Option(False, "--trace", help="Enable trace-level logging"),
    quiet: bool = typer.Option(False, "--quiet", "-q")
):
    if trace:
        setup_logging(level="TRACE")  # Even more verbose than DEBUG
```

Trace level would include:
- All DEBUG logs
- Function entry/exit with arguments
- Data structure dumps
- Performance counters

---

## Files Requiring Enhancement

| File | Priority | Changes |
|------|----------|---------|
| `kosmos/agents/research_director.py` | Critical | Phase decisions, agent coordination |
| `kosmos/cli/commands/run.py` | Critical | Iteration progress, timing |
| `kosmos/core/providers/anthropic.py` | High | LLM call details |
| `kosmos/core/providers/openai_provider.py` | High | LLM call details |
| `kosmos/agents/base.py` | Medium | Message routing |
| `kosmos/core/workflow.py` | Medium | State transitions |
| `kosmos/orchestration/*.py` | Low | Plan creation/review |

---

## Implementation Guidelines

### Logging Patterns

```python
# Phase transitions
logger.debug(f"[{self.agent_id}] Phase: {old} -> {new}, trigger: {trigger}")

# LLM calls
logger.debug(f"[LLM] {model}: {input_tokens}in/{output_tokens}out, {latency_ms}ms")

# Iteration progress
logger.debug(f"[Iter {i}] hyps={n_hyps}, exps={n_exps}, time={elapsed:.1f}s")

# Agent messages
logger.debug(f"[MSG] {src} -> {dst}: {msg_type}, id={msg_id}")
```

### Performance Considerations

- Use lazy string formatting: `logger.debug("x=%s", x)` not `logger.debug(f"x={x}")`
- Gate expensive computations: `if logger.isEnabledFor(logging.DEBUG):`
- Avoid logging large data structures without truncation

---

## Related Issues

- Issue #34: Research timeout - would benefit from iteration timing logs
- Issue #33: Async/sync mismatch - now fixed, but DEBUG logs would have shown mock fallbacks

---

*Analysis Date: 2025-11-29*
