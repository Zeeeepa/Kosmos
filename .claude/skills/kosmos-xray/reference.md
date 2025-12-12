# Kosmos X-Ray Reference

Detailed API documentation for all X-Ray tools.

## mapper.py

### Purpose
Maps directory structure with token estimates. Identifies large files that may consume excessive context.

### Usage
```
python mapper.py [directory] [--json] [--summary]
```

### Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `directory` | string | `.` | Directory to map |
| `--json` | flag | - | Output as JSON |
| `--summary` | flag | - | Summary only, no tree |

### Output Format (Text)
```
ROOT: kosmos/
    workflow/
        research_loop.py (8.2K tok)
        __init__.py (50 tok)
    agents/
        base.py (4.1K tok) [MEDIUM]
        registry.py (12.5K tok) [!LARGE]

============================================================
SUMMARY
  Total files: 156
  Total tokens: 245K
  Context budget: ~122.5% of 200K window

LARGE FILES (>10K tokens) - Consider using skeleton.py instead:
   12.5K tok  agents/registry.py
   ...
```

### Output Format (JSON)
```json
{
  "path": "/mnt/c/python/kosmos",
  "total_tokens": 245000,
  "file_count": 156,
  "tree": ["ROOT: kosmos/", "    workflow/", ...],
  "large_files": [
    {"path": "agents/registry.py", "tokens": 12500, "formatted": "12.5K"}
  ]
}
```

---

## skeleton.py

### Purpose
Extracts Python file interfaces via AST parsing. Achieves ~95% token reduction by showing only signatures and docstring summaries.

### Usage
```
python skeleton.py <path> [--pattern GLOB] [--priority LEVEL] [--private] [--json]
```

### Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `path` | string | required | File or directory to analyze |
| `--pattern` | string | - | Glob pattern filter (e.g., `**/base*.py`) |
| `--priority` | choice | - | Filter by priority: critical, high, medium, low |
| `--private` | flag | - | Include _private methods |
| `--json` | flag | - | Output as JSON |

### Priority Levels
Defined in `configs/priority_modules.json`:

| Level | Patterns | Description |
|-------|----------|-------------|
| critical | `**/workflow/**/*.py`, `**/agents/base*.py` | Core orchestration |
| high | `**/world_model/**/*.py`, `**/execution/**/*.py` | Domain logic |
| medium | `**/validation/**/*.py`, `**/streaming/**/*.py` | Infrastructure |
| low | `**/utils/**/*.py`, `**/tests/**/*.py` | Utilities |

### Output Format (Text)
```
# ============================================================
# FILE: kosmos/workflow/research_loop.py
# Tokens: 8200 -> 410 (95.0% reduction)
# ============================================================
"""Main research workflow orchestration..."""

class ResearchWorkflow:
    """Orchestrates autonomous research cycles..."""

    def __init__(self, config: ResearchConfig): ...
        """Initialize the research workflow..."""

    async def run(self, goal: str) -> ResearchResults: ...
        """Execute the full research workflow..."""

    async def _execute_cycle(self, cycle_num: int) -> CycleResult: ...
        """Execute a single research cycle..."""
```

### Output Format (JSON)
```json
{
  "files": [
    {
      "file": "kosmos/workflow/research_loop.py",
      "original_tokens": 8200,
      "skeleton_tokens": 410,
      "reduction": "95.0%",
      "skeleton": "class ResearchWorkflow:..."
    }
  ],
  "summary": {
    "file_count": 1,
    "total_original_tokens": 8200,
    "total_skeleton_tokens": 410,
    "overall_reduction": "95.0%"
  }
}
```

---

## dependency_graph.py

### Purpose
Analyzes import relationships between Python modules. Identifies architectural layers and circular dependencies.

### Usage
```
python dependency_graph.py [directory] [--root PACKAGE] [--focus STRING] [--json]
```

### Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `directory` | string | `.` | Directory to analyze |
| `--root` | string | - | Root package name (e.g., `kosmos`) |
| `--focus` | string | - | Focus on modules matching this string |
| `--json` | flag | - | Output as JSON |

### Architectural Layers
The tool automatically categorizes modules:

| Layer | Criteria | Description |
|-------|----------|-------------|
| **foundation** | High imported_by, low imports | Base classes, utilities |
| **core** | Balanced | Domain logic |
| **orchestration** | Low imported_by, high imports | Coordination, workflows |
| **leaf** | Minimal interaction | Standalone modules |

### Output Format (Text)
```
======================================================================
KOSMOS DEPENDENCY GRAPH
======================================================================

ARCHITECTURAL LAYERS:
----------------------------------------

  ORCHESTRATION (3 modules):
    kosmos.workflow.research_loop
      imported by: 2 | imports: 12
    kosmos.orchestration.delegation
      imported by: 1 | imports: 8

  FOUNDATION (5 modules):
    kosmos.agents.base
      imported by: 15 | imports: 2
    kosmos.core.types
      imported by: 12 | imports: 0

CIRCULAR DEPENDENCIES (potential issues):
----------------------------------------
  kosmos.agents.registry <-> kosmos.agents.base

======================================================================
SUMMARY
  Total modules: 45
  Internal dependencies: 120
  Circular dependencies: 1
  External packages: 15
    Top: asyncio, dataclasses, json, logging, pathlib...
```

### Output Format (JSON)
```json
{
  "modules": {
    "kosmos.workflow.research_loop": {
      "imports": ["kosmos.agents.base", "kosmos.world_model.storage"],
      "imported_by": ["kosmos.cli.main"]
    }
  },
  "layers": {
    "foundation": ["kosmos.agents.base", "kosmos.core.types"],
    "core": ["kosmos.world_model.storage"],
    "orchestration": ["kosmos.workflow.research_loop"],
    "leaf": ["kosmos.cli.main"]
  },
  "circular_dependencies": [["kosmos.agents.base", "kosmos.agents.registry"]],
  "external_dependencies": {
    "kosmos.workflow.research_loop": ["asyncio", "logging"]
  },
  "summary": {
    "total_modules": 45,
    "internal_edges": 120,
    "circular_count": 1
  }
}
```

---

## Library Modules

### lib/token_estimator.py

| Function | Signature | Description |
|----------|-----------|-------------|
| `estimate_tokens` | `(text: str) -> int` | Estimate tokens for string |
| `estimate_file_tokens` | `(filepath: str) -> int` | Estimate tokens for file |
| `categorize_size` | `(tokens: int) -> str` | Get size category tag |
| `format_token_count` | `(tokens: int) -> str` | Format for display |

### lib/ast_utils.py

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_skeleton` | `(filepath: str, include_private: bool) -> str` | Extract file skeleton |
| `parse_imports` | `(filepath: str) -> Tuple[List, List]` | Parse absolute/relative imports |
| `get_class_hierarchy` | `(filepath: str) -> Dict[str, List]` | Extract class inheritance |

---

## Configuration Files

### configs/ignore_patterns.json
```json
{
  "directories": ["artifacts", "__pycache__", ".git", ...],
  "extensions": [".pyc", ".log", ".pkl", ...],
  "files": ["*.log", "*.jsonl", ...]
}
```

### configs/priority_modules.json
```json
{
  "priority_patterns": {
    "critical": {"patterns": ["**/workflow/**/*.py", ...]},
    "high": {"patterns": ["**/world_model/**/*.py", ...]},
    ...
  },
  "architecture_keywords": {
    "class_patterns": ["Workflow", "Manager", "Base", ...],
    "method_patterns": ["run", "execute", "process", ...]
  }
}
```
