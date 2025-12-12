# Kosmos: Developer Warm Start

> Context-efficient onboarding guide for AI programmers.
> Generated: 2025-12-12
> Codebase: 188 files, ~692K tokens (use X-Ray tools to stay under budget)

---

## 1. System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                        KOSMOS ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User Goal                                                      │
│       │                                                          │
│       ▼                                                          │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│   │  Research   │────▶│    Plan     │────▶│  Delegation │       │
│   │  Workflow   │     │  Creator    │     │   Manager   │       │
│   └─────────────┘     └─────────────┘     └─────────────┘       │
│         │                   │                   │                │
│         │                   ▼                   ▼                │
│         │           ┌─────────────┐     ┌─────────────┐         │
│         │           │    Plan     │     │   Agents    │         │
│         │           │  Reviewer   │     │  (Various)  │         │
│         │           └─────────────┘     └─────────────┘         │
│         │                                     │                  │
│         ▼                                     ▼                  │
│   ┌─────────────┐                     ┌─────────────┐           │
│   │  Artifact   │◀────────────────────│    Code     │           │
│   │   State     │                     │  Executor   │           │
│   │  Manager    │                     │  (Sandbox)  │           │
│   └─────────────┘                     └─────────────┘           │
│         │                                                        │
│         ▼                                                        │
│   ┌─────────────┐     ┌─────────────┐                           │
│   │   World     │◀───▶│  Knowledge  │                           │
│   │   Model     │     │   Graph     │                           │
│   └─────────────┘     └─────────────┘                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Overview

Kosmos is an autonomous scientific research framework that operates in iterative cycles:

**Hypothesis → Plan → Execute → Validate → Compress → Repeat**

Key architectural concepts:
- **Multi-agent coordination** via message passing (async queues)
- **Code sandbox** for safe execution (Docker isolation)
- **Knowledge graph** for persistent world model (Neo4j/SQLite)
- **Real-time streaming** via EventBus pub/sub pattern
- **Context compression** to manage token budgets across cycles

---

## 3. Critical Classes

### Entry Points
| Class | Location | Purpose |
|-------|----------|---------|
| `ResearchWorkflow` | `kosmos/workflow/research_loop.py` | Main orchestrator - call `run()` |
| CLI | `kosmos/cli/main.py` | Command-line interface |
| API | `kosmos/api/` | REST/SSE/WebSocket endpoints |

### Core Components
| Class | Location | Purpose |
|-------|----------|---------|
| `BaseAgent` | `kosmos/agents/base.py` | Agent base class with messaging |
| `AgentRegistry` | `kosmos/agents/registry.py` | Agent discovery and management |
| `DelegationManager` | `kosmos/orchestration/delegation.py` | Task routing to agents |
| `PlanCreatorAgent` | `kosmos/orchestration/plan_creator.py` | Generates research plans |
| `PlanReviewerAgent` | `kosmos/orchestration/plan_reviewer.py` | Validates plans |

### Execution Layer
| Class | Location | Purpose |
|-------|----------|---------|
| `CodeExecutor` | `kosmos/execution/code_executor.py` | Run Python/R code |
| `RetryStrategy` | `kosmos/execution/retry_strategy.py` | Error recovery |
| `DockerSandbox` | `kosmos/sandbox/docker_sandbox.py` | Isolated execution |

### Data Layer
| Class | Location | Purpose |
|-------|----------|---------|
| `ArtifactStateManager` | `kosmos/world_model/artifacts.py` | Finding persistence |
| `WorldModelStorage` | `kosmos/world_model/storage.py` | Graph storage interface |
| `Finding` | `kosmos/world_model/artifacts.py` | Research finding dataclass |
| `Hypothesis` | `kosmos/models/hypothesis.py` | Hypothesis dataclass |

### Foundation (Most Imported)
| Module | Imported By | Purpose |
|--------|-------------|---------|
| `kosmos.config` | 48 modules | Configuration management |
| `kosmos.models.hypothesis` | 26 modules | Core data model |
| `kosmos.literature.base_client` | 20 modules | Literature search base |
| `kosmos.core.llm` | 12 modules | LLM client abstraction |

---

## 4. Data Flow

```
User Query
    │
    ▼
[1] ResearchWorkflow.run(goal)
    │
    ├──▶ [2] state_manager.get_cycle_context()
    │         │
    ├──▶ [3] plan_creator.create_plan(objective, context)
    │         │
    ├──▶ [4] novelty_detector.check_plan_novelty(plan)
    │         │
    ├──▶ [5] plan_reviewer.review_plan(plan, context)
    │         │
    │    [if approved]
    │         │
    ├──▶ [6] delegation_manager.execute_plan(plan)
    │         │
    │         └──▶ [7] agent.process_task(task)
    │                   │
    │                   └──▶ [8] code_executor.execute(code)
    │                             │
    │                             └──▶ [9] sandbox.run(code)
    │
    ├──▶ [10] scholar_eval.evaluate_finding(result)
    │
    ├──▶ [11] state_manager.save_finding_artifact(finding)
    │
    └──▶ [12] context_compressor.compress_cycle_results()
              │
              ▼
         Next Cycle (repeat 1-12)
              │
              ▼
         Final Results + Discoveries
```

---

## 5. Entry Points

### CLI Commands
```bash
# Run research workflow
kosmos run "research objective" --cycles 5

# With streaming output
kosmos run "objective" --stream

# Health check
kosmos doctor

# Interactive mode
kosmos interactive
```

### Python API
```python
from kosmos.workflow import ResearchWorkflow

# Basic usage
workflow = ResearchWorkflow(
    research_objective="Investigate X",
    max_cycles=20
)
results = await workflow.run(num_cycles=5)

# With configuration
from kosmos.config import KosmosConfig
config = KosmosConfig.from_env()
```

### Key Imports
```python
# Workflow
from kosmos.workflow import ResearchWorkflow

# Agents
from kosmos.agents.base import BaseAgent
from kosmos.agents.registry import AgentRegistry

# Execution
from kosmos.execution.code_executor import CodeExecutor

# Data models
from kosmos.models.hypothesis import Hypothesis
from kosmos.world_model.artifacts import Finding, ArtifactStateManager

# Configuration
from kosmos.config import KosmosConfig
```

---

## 6. Context Hazards

**DO NOT READ these directories/files** - they consume context without providing architectural insight:

### Large Data Directories
| Directory | Reason |
|-----------|--------|
| `artifacts/` | Runtime outputs, plots, logs |
| `data/` | Test datasets |
| `.literature_cache/` | Cached PDF content |
| `kosmos-reference/` | Reference PDFs |
| `logs/` | Execution logs |
| `archive/` | Archived documentation |

### Large Files (>10K tokens)
| File | Tokens | Use Skeleton Instead |
|------|--------|---------------------|
| `agents/research_director.py` | 21.3K | `skeleton.py` |
| `workflow/ensemble.py` | 10.7K | `skeleton.py` |
| `execution/data_analysis.py` | 10.6K | `skeleton.py` |

### File Extensions to Skip
`.jsonl`, `.log`, `.pkl`, `.pickle`, `.pyc`, `.coverage`, `.sqlite`

---

## 7. Quick Verification

```bash
# Check system health
kosmos doctor

# Verify imports
python -c "from kosmos.workflow import ResearchWorkflow; print('OK')"

# Run quick sanity tests
pytest tests/ -k "sanity" --tb=short -q

# Check database
python -c "from kosmos.db import get_engine; print('DB OK')"
```

---

## 8. X-Ray Commands

Use these scripts to explore further without consuming full context:

```bash
# Map directory structure with token estimates
python .claude/skills/kosmos-xray/scripts/mapper.py kosmos/ --summary

# Extract class/method skeletons (95% token reduction)
python .claude/skills/kosmos-xray/scripts/skeleton.py kosmos/workflow/

# Filter by priority level
python .claude/skills/kosmos-xray/scripts/skeleton.py kosmos/ --priority critical

# Analyze import dependencies
python .claude/skills/kosmos-xray/scripts/dependency_graph.py kosmos/ --root kosmos

# Focus on specific area
python .claude/skills/kosmos-xray/scripts/dependency_graph.py kosmos/ --focus workflow
```

### Token Budget Reference
| Operation | Tokens | Use When |
|-----------|--------|----------|
| mapper.py --summary | ~500 | First exploration |
| skeleton.py (1 file) | ~200-500 | Understanding interface |
| skeleton.py --priority critical | ~5K | Core architecture |
| dependency_graph.py | ~3K | Import relationships |

---

## 9. Architectural Layers

Based on dependency analysis:

### Foundation (High reuse, few dependencies)
- `kosmos.config` - Configuration
- `kosmos.models.hypothesis` - Core data model
- `kosmos.core.events` - Event system
- `kosmos.core.providers.base` - LLM provider base

### Core (Balanced)
- `kosmos.core.llm` - LLM client
- `kosmos.knowledge.graph` - Knowledge graph
- `kosmos.world_model.interface` - World model

### Orchestration (Many imports, coordinates system)
- `kosmos.workflow.research_loop` - Main workflow
- `kosmos.agents.research_director` - Agent coordination
- `kosmos.orchestration.delegation` - Task dispatch

---

*Generated by kosmos_architect using kosmos-xray skill.*
*To refresh: `@kosmos_architect refresh`*
