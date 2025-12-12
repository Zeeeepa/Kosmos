# Kosmos X-Ray Cheatsheet

Quick reference for context-efficient codebase exploration.

## Commands

```bash
# Directory mapping
mapper.py [dir]              # Full tree with token counts
mapper.py --summary          # Summary only
mapper.py --json             # Machine-readable output

# Skeleton extraction
skeleton.py <file>           # Single file interface
skeleton.py <dir>            # All .py files in directory
skeleton.py <dir> --pattern "*.py"   # Pattern filter
skeleton.py <dir> --priority critical  # Priority filter
skeleton.py --private        # Include _private methods
skeleton.py --json           # JSON output

# Dependency graph
dependency_graph.py [dir]    # Analyze imports
dependency_graph.py --root kosmos  # Set root package
dependency_graph.py --focus workflow  # Focus on subset
dependency_graph.py --json   # JSON output
```

## Priority Levels

| Level | What | When |
|-------|------|------|
| **critical** | Orchestration, workflows | Understand system flow |
| **high** | Domain logic, data models | Deep feature work |
| **medium** | Infrastructure, validation | Supporting changes |
| **low** | Utils, tests, CLI | Only when needed |

## Context Hazards (DO NOT READ)

```
artifacts/           # Runtime outputs
data/                # Test datasets
.literature_cache/   # PDF caches
kosmos-reference/    # Reference PDFs
logs/                # Execution logs
*.jsonl, *.pkl       # Large data files
```

## Token Budget Reference

| File Size | Raw Tokens | Skeleton Tokens | Reduction |
|-----------|-----------|-----------------|-----------|
| 10KB | ~2,500 | ~125 | 95% |
| 50KB | ~12,500 | ~625 | 95% |
| 100KB | ~25,000 | ~1,250 | 95% |

## Quick Exploration Path

```bash
# 1. Get overview (500 tokens)
python .claude/skills/kosmos-xray/scripts/mapper.py --summary

# 2. Find critical files (2K tokens)
python .claude/skills/kosmos-xray/scripts/skeleton.py kosmos/ --priority critical

# 3. Understand dependencies (2K tokens)
python .claude/skills/kosmos-xray/scripts/dependency_graph.py kosmos/ --root kosmos

# Total: ~4.5K tokens for full architecture understanding
```

## Using with Agent

```
@kosmos_architect generate    # Create WARM_START.md
@kosmos_architect refresh     # Update existing doc
@kosmos_architect query "X"   # Answer specific question
```
