# Debug Mode Guide

Kosmos includes comprehensive debug instrumentation for diagnosing issues, understanding execution flow, and troubleshooting research runs.

## Quick Start

For most debugging scenarios, use the `--trace` flag:

```bash
kosmos run --trace --objective "Your research question" --max-iterations 2
```

This enables maximum verbosity including:
- All debug log messages
- LLM call logging (requests/responses)
- Agent message routing
- Workflow state transitions
- Real-time stage tracking

## Debug Levels

Debug verbosity is controlled by levels 0-3:

| Level | Name | What's Logged | Use Case |
|-------|------|---------------|----------|
| 0 | Off | Standard INFO/WARNING/ERROR only | Production runs |
| 1 | Critical Path | Decision points, action execution, phase transitions | Basic debugging |
| 2 | Full Trace | All of level 1 + LLM calls, message routing, timing | Deep debugging |
| 3 | Data Dumps | All of level 2 + full payloads, state snapshots | Issue reproduction |

## Environment Variables

Configure debug mode via environment variables in your `.env` file:

```bash
# Core debug settings
DEBUG_MODE=true                    # Master debug switch
DEBUG_LEVEL=2                      # Verbosity level (0-3)
DEBUG_MODULES=research_director,workflow  # Comma-separated module filter (optional)

# Specific logging toggles
LOG_LLM_CALLS=true                 # Log LLM request/response summaries
LOG_AGENT_MESSAGES=true            # Log inter-agent message routing
LOG_WORKFLOW_TRANSITIONS=true      # Log state machine transitions with timing

# Stage tracking (real-time observability)
STAGE_TRACKING_ENABLED=true        # Enable stage tracking output
STAGE_TRACKING_FILE=logs/stages.jsonl  # Output file path
```

## CLI Flags

All debug settings can be overridden via CLI flags:

```bash
# Enable trace mode (maximum verbosity)
kosmos run --trace --objective "..."

# Set specific debug level
kosmos run --debug-level 2 --objective "..."

# Debug specific modules only
kosmos run --debug --debug-modules "research_director,workflow" --objective "..."

# Combine with quiet mode (suppress Rich formatting, keep debug logs)
kosmos run --trace --quiet --objective "..."
```

| Flag | Short | Description |
|------|-------|-------------|
| `--debug` | | Enable debug mode (level 1) |
| `--trace` | | Enable trace mode (level 3, all toggles on) |
| `--debug-level N` | `-dl N` | Set specific debug level (0-3) |
| `--debug-modules M` | | Comma-separated list of modules to debug |
| `--verbose` | `-v` | Enable verbose output (INFO level) |
| `--quiet` | `-q` | Suppress non-essential console output |

## Understanding Debug Output

### Decision Logging (`[DECISION]`)

Shows research director decision-making:

```
[DECISION] decide_next_action: state=ANALYZING, iteration=2/10, hypotheses=3, untested=1, experiments_queued=0
```

Fields:
- `state`: Current workflow state
- `iteration`: Current/max iteration count
- `hypotheses`: Total hypotheses generated
- `untested`: Hypotheses not yet tested
- `experiments_queued`: Pending experiments

### Action Logging (`[ACTION]`)

Shows action execution:

```
[ACTION] Executing: GENERATE_HYPOTHESIS
```

### Agent Message Logging (`[MSG]`)

Shows inter-agent communication (enable with `LOG_AGENT_MESSAGES=true` or `--trace`):

```
[MSG] research_director -> hypothesis_generator: type=REQUEST, correlation_id=abc123, content_preview={"task": "generate"...
[MSG] hypothesis_generator <- research_director: type=REQUEST, msg_id=abc123
```

Fields:
- `->`: Outgoing message (sender -> recipient)
- `<-`: Incoming message (recipient <- sender)
- `type`: Message type (REQUEST, RESPONSE, NOTIFICATION, ERROR)
- `correlation_id`: Links request/response pairs
- `msg_id`: Unique message identifier
- `content_preview`: First 100 chars of message content (outgoing only)

### Workflow Transitions (`[WORKFLOW]`)

Shows state machine transitions with timing:

```
[WORKFLOW] Transition: HYPOTHESIZING -> DESIGNING (was in HYPOTHESIZING for 12.34s) action='hypothesis_complete'
```

### LLM Call Logging (`[LLM]`)

Shows LLM API interactions:

```
[LLM] Request: model=claude-sonnet-4-5-20241022, prompt_len=2456, system_len=890, max_tokens=4096, temp=0.70
[LLM] Response: model=claude-sonnet-4-5-20241022, in_tokens=3346, out_tokens=1205, latency=4521ms, finish=end_turn
```

### Iteration Summary (`[ITER]`)

Shows per-iteration progress:

```
[ITER 2/10] state=ANALYZING, hyps=3, exps=2, duration=45.67s
```

## Stage Tracking

Stage tracking provides structured JSON output for programmatic analysis and real-time monitoring.

### Enabling Stage Tracking

```bash
# Via environment
STAGE_TRACKING_ENABLED=true
STAGE_TRACKING_FILE=logs/stages.jsonl

# Via CLI (--trace enables automatically)
kosmos run --trace --objective "..."
```

### Stage Output Format

Each stage event is written as a JSON line to `logs/stages.jsonl`:

```json
{
  "timestamp": "2025-11-29T14:23:45.123Z",
  "process_id": "research_1732889025",
  "stage": "GENERATE_HYPOTHESIS",
  "status": "completed",
  "duration_ms": 3456,
  "iteration": 2,
  "parent_stage": "RESEARCH_ITERATION",
  "substage": null,
  "output_summary": null,
  "error": null,
  "metadata": {"hypothesis_count": 3}
}
```

### Viewing Stage Events

```bash
# Watch stages in real-time
tail -f logs/stages.jsonl | jq .

# Filter for failed stages
cat logs/stages.jsonl | jq 'select(.status == "failed")'

# Get timing summary
cat logs/stages.jsonl | jq 'select(.status == "completed") | {stage, duration_ms}'

# Count stages by type
cat logs/stages.jsonl | jq -s 'group_by(.stage) | map({stage: .[0].stage, count: length})'
```

### Programmatic Access

```python
from kosmos.core.stage_tracker import get_stage_tracker

# Get tracker instance
tracker = get_stage_tracker()

# Get all recorded events
events = tracker.get_events()

# Get summary statistics
summary = tracker.get_summary()
print(f"Total stages: {summary['total_stages']}")
print(f"Completed: {summary['completed']}")
print(f"Failed: {summary['failed']}")
print(f"Total duration: {summary['total_duration_ms']}ms")
```

## Troubleshooting Common Issues

### Research Loop Stalls

Enable full trace to identify where execution stops:

```bash
kosmos run --trace --objective "..." --max-iterations 3 2>&1 | tee debug.log
```

Look for:
- Last `[DECISION]` entry to see decision state
- Missing `[ACTION]` after `[DECISION]` indicates decision logic issue
- Long gaps in `[LLM]` responses may indicate API timeouts

### LLM Errors

Enable LLM call logging:

```bash
LOG_LLM_CALLS=true kosmos run --debug --objective "..."
```

Check for:
- Token count approaching limits
- High latency responses
- Unexpected finish reasons

### Workflow Stuck in State

Enable workflow transition logging:

```bash
LOG_WORKFLOW_TRANSITIONS=true kosmos run --debug-level 2 --objective "..."
```

Look for:
- Repeated transitions to same state
- Long duration in single state
- Missing expected transitions

## Log File Locations

| File | Content |
|------|---------|
| `logs/kosmos.log` | Main application log |
| `logs/stages.jsonl` | Stage tracking events (JSON lines) |
| `~/.kosmos/logs/` | CLI-specific logs |

## Performance Considerations

Debug logging adds overhead. For production runs:

```bash
# Minimal logging (recommended for long runs)
DEBUG_LEVEL=0 kosmos run --objective "..." --max-iterations 20

# Monitor progress without full debug
STAGE_TRACKING_ENABLED=true DEBUG_LEVEL=0 kosmos run --objective "..."
```

Stage tracking alone (without full debug logging) adds minimal overhead and is suitable for production monitoring.
