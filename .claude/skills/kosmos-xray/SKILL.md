---
name: kosmos-xray
description: Context-efficient codebase exploration using AST analysis. Use when exploring Kosmos architecture, understanding code structure, or preparing documentation for AI programmers. Triggers: xray, map structure, skeleton, interface, architecture, explore kosmos, warm start, token budget, context compression.
---

# Kosmos X-Ray Skill

Specialized tools for analyzing the Kosmos codebase efficiently within limited context windows. Uses AST parsing to extract structural information (classes, methods, signatures) without loading implementation details, achieving ~95% token reduction.

## When to Use This Skill

- **Exploring the codebase** - Map directory structure before diving into files
- **Understanding architecture** - Extract class hierarchies and dependencies
- **Onboarding** - Generate documentation for new AI programmers
- **Context management** - Identify large files that should use skeleton view instead of full read

## Core Tools

### 1. mapper.py - Directory Structure Map

Shows file tree with token estimates. Identifies context hazards (large files).

```bash
# Map entire project
python .claude/skills/kosmos-xray/scripts/mapper.py

# Map specific directory
python .claude/skills/kosmos-xray/scripts/mapper.py kosmos/workflow/

# Get summary only (no tree)
python .claude/skills/kosmos-xray/scripts/mapper.py --summary

# JSON output for parsing
python .claude/skills/kosmos-xray/scripts/mapper.py --json
```

### 2. skeleton.py - Interface Extraction

Extracts Python file skeletons via AST. Shows classes, methods, signatures without implementations.

```bash
# Single file skeleton
python .claude/skills/kosmos-xray/scripts/skeleton.py kosmos/workflow/research_loop.py

# Directory with pattern filter
python .claude/skills/kosmos-xray/scripts/skeleton.py kosmos/ --pattern "**/base*.py"

# Filter by priority (critical, high, medium, low)
python .claude/skills/kosmos-xray/scripts/skeleton.py kosmos/ --priority critical

# Include private methods
python .claude/skills/kosmos-xray/scripts/skeleton.py kosmos/agents/ --private
```

### 3. dependency_graph.py - Import Analysis

Maps import relationships between modules. Identifies architectural layers and circular dependencies.

```bash
# Analyze dependencies
python .claude/skills/kosmos-xray/scripts/dependency_graph.py kosmos/

# With root package name
python .claude/skills/kosmos-xray/scripts/dependency_graph.py kosmos/ --root kosmos

# Focus on specific area
python .claude/skills/kosmos-xray/scripts/dependency_graph.py kosmos/ --focus workflow
```

## Recommended Workflow

1. **Survey first** - Run mapper.py to see what exists
2. **Identify priorities** - Check configs/priority_modules.json for guidance
3. **X-ray critical files** - Use skeleton.py on important modules
4. **Map dependencies** - Understand relationships with dependency_graph.py
5. **Read selectively** - Only read full implementation when needed

## Integration with kosmos_architect Agent

This skill is automatically loaded by the `kosmos_architect` agent. You can also use it directly for targeted analysis.

```
# Use the agent for full onboarding documentation
@kosmos_architect generate

# Or use individual tools directly
@kosmos-xray Map the workflow directory
```

## Configuration Files

- `configs/ignore_patterns.json` - Directories and files to skip
- `configs/priority_modules.json` - Module priority levels and patterns

## Context Budget Guidelines

| Operation | Typical Tokens | Use When |
|-----------|---------------|----------|
| mapper.py summary | ~500 | First exploration |
| mapper.py full | ~2-5K | Understanding structure |
| skeleton.py (1 file) | ~200-500 | Understanding interface |
| skeleton.py (directory) | ~2-10K | Learning a subsystem |
| dependency_graph.py | ~1-3K | Architecture analysis |
| Full file read | Varies | Need implementation details |

For detailed API documentation, see [reference.md](reference.md).
For quick command reference, see [CHEATSHEET.md](CHEATSHEET.md).
