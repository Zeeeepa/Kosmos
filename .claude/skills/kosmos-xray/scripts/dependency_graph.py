#!/usr/bin/env python3
"""
Kosmos Dependency Graph Generator

Analyzes import relationships between Python modules.
Identifies core modules, circular dependencies, and architectural layers.

Usage:
    python dependency_graph.py [directory] [options]

Examples:
    python dependency_graph.py kosmos/
    python dependency_graph.py kosmos/ --root kosmos
    python dependency_graph.py kosmos/ --focus workflow
    python dependency_graph.py kosmos/ --json
"""

import argparse
import ast
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# Find the skill root directory
SCRIPT_DIR = Path(__file__).parent
SKILL_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = SKILL_ROOT / "configs"


def load_ignore_patterns() -> Set[str]:
    """Load directory ignore patterns from config."""
    config_path = CONFIG_DIR / "ignore_patterns.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        return set(config.get("directories", []))
    return {"__pycache__", ".git", "tests"}


def parse_imports(filepath: str) -> Tuple[List[str], List[str]]:
    """
    Parse imports from a Python file.

    Returns:
        Tuple of (absolute_imports, relative_imports)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
    except Exception:
        return [], []

    absolute_imports = []
    relative_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                absolute_imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level > 0:
                prefix = "." * node.level
                relative_imports.append(f"{prefix}{module}")
            else:
                absolute_imports.append(module)

    return absolute_imports, relative_imports


def module_path_to_name(filepath: str, root_dir: str) -> str:
    """Convert file path to module name."""
    rel_path = os.path.relpath(filepath, root_dir)
    # Remove .py extension and convert path separators
    module = rel_path.replace(os.sep, ".").replace("/", ".")
    if module.endswith(".py"):
        module = module[:-3]
    if module.endswith(".__init__"):
        module = module[:-9]
    return module


def resolve_relative_import(
    importing_module: str,
    relative_import: str
) -> str:
    """Resolve a relative import to absolute module name."""
    # Count leading dots
    level = 0
    while relative_import.startswith("."):
        level += 1
        relative_import = relative_import[1:]

    # Go up 'level' packages
    parts = importing_module.split(".")
    if level > len(parts):
        return relative_import  # Can't resolve

    base = ".".join(parts[:-level]) if level > 0 else importing_module
    if relative_import:
        return f"{base}.{relative_import}" if base else relative_import
    return base


def build_dependency_graph(
    directory: str,
    root_package: Optional[str] = None
) -> Dict:
    """
    Build a dependency graph for all Python files.

    Returns dict with:
    {
        "modules": {module: {"file": path, "imports": [...], "imported_by": [...]}},
        "internal_edges": [(from, to), ...],
        "external_deps": {module: [external_imports]},
        "circular": [(a, b), ...]
    }
    """
    ignore_dirs = load_ignore_patterns()

    # First pass: discover all modules
    modules = {}
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in files:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(root, filename)
            module_name = module_path_to_name(filepath, directory)

            if root_package:
                module_name = f"{root_package}.{module_name}"

            modules[module_name] = {
                "file": filepath,
                "imports": [],
                "imported_by": []
            }

    # Second pass: analyze imports
    internal_edges = []
    external_deps = defaultdict(set)

    for module_name, info in modules.items():
        abs_imports, rel_imports = parse_imports(info["file"])

        # Process absolute imports
        for imp in abs_imports:
            # Get base module (first component)
            base = imp.split(".")[0]

            # Check if it's an internal import
            is_internal = False
            for known_module in modules:
                if imp == known_module or known_module.startswith(f"{imp}.") or imp.startswith(f"{known_module}."):
                    is_internal = True
                    # Find the most specific match
                    target = imp
                    while target and target not in modules:
                        target = ".".join(target.split(".")[:-1])

                    if target and target != module_name:
                        info["imports"].append(target)
                        modules[target]["imported_by"].append(module_name)
                        internal_edges.append((module_name, target))
                    break

            if not is_internal:
                external_deps[module_name].add(base)

        # Process relative imports
        for rel_imp in rel_imports:
            resolved = resolve_relative_import(module_name, rel_imp)
            # Find matching module
            target = resolved
            while target and target not in modules:
                target = ".".join(target.split(".")[:-1])

            if target and target != module_name:
                info["imports"].append(target)
                modules[target]["imported_by"].append(module_name)
                internal_edges.append((module_name, target))

    # Find circular dependencies
    circular = []
    seen_pairs = set()
    for a, b in internal_edges:
        if (b, a) in seen_pairs:
            circular.append((min(a, b), max(a, b)))
        seen_pairs.add((a, b))
    circular = list(set(circular))

    return {
        "modules": modules,
        "internal_edges": internal_edges,
        "external_deps": {k: list(v) for k, v in external_deps.items()},
        "circular": circular
    }


def identify_layers(graph: Dict) -> Dict[str, List[str]]:
    """
    Identify architectural layers based on import patterns.

    Modules that are imported by many others = core/foundation
    Modules that import many others = orchestration/high-level
    """
    modules = graph["modules"]

    # Score modules by import patterns
    scores = {}
    for name, info in modules.items():
        imported_by_count = len(info["imported_by"])
        imports_count = len(info["imports"])

        # High imported_by, low imports = foundation
        # Low imported_by, high imports = orchestration
        scores[name] = {
            "imported_by": imported_by_count,
            "imports": imports_count,
            "ratio": imported_by_count / (imports_count + 1)
        }

    # Categorize
    layers = {
        "foundation": [],  # Imported by many, imports few
        "core": [],        # Balance of both
        "orchestration": [],  # Imports many, imported by few
        "leaf": []         # Little interaction
    }

    for name, score in scores.items():
        if score["imported_by"] == 0 and score["imports"] == 0:
            layers["leaf"].append(name)
        elif score["ratio"] > 2:
            layers["foundation"].append(name)
        elif score["ratio"] < 0.5 and score["imports"] > 2:
            layers["orchestration"].append(name)
        else:
            layers["core"].append(name)

    # Sort by import count within each layer
    for layer in layers:
        layers[layer].sort(key=lambda x: scores[x]["imported_by"], reverse=True)

    return layers


def print_text_graph(graph: Dict, focus: Optional[str] = None):
    """Print a text-based dependency graph."""
    modules = graph["modules"]
    layers = identify_layers(graph)

    print("=" * 70)
    print("KOSMOS DEPENDENCY GRAPH")
    print("=" * 70)
    print()

    # Print layers
    print("ARCHITECTURAL LAYERS:")
    print("-" * 40)
    for layer_name, layer_modules in layers.items():
        if layer_modules:
            print(f"\n  {layer_name.upper()} ({len(layer_modules)} modules):")
            for mod in layer_modules[:10]:  # Top 10 per layer
                info = modules[mod]
                print(f"    {mod}")
                print(f"      imported by: {len(info['imported_by'])} | imports: {len(info['imports'])}")

    # Circular dependencies
    if graph["circular"]:
        print()
        print("CIRCULAR DEPENDENCIES (potential issues):")
        print("-" * 40)
        for a, b in graph["circular"]:
            print(f"  {a} <-> {b}")

    # Focus mode
    if focus:
        print()
        print(f"FOCUS: modules matching '{focus}'")
        print("-" * 40)
        for name, info in modules.items():
            if focus.lower() in name.lower():
                print(f"\n  {name}")
                if info["imports"]:
                    print(f"    imports:")
                    for imp in sorted(info["imports"]):
                        print(f"      <- {imp}")
                if info["imported_by"]:
                    print(f"    imported by:")
                    for imp in sorted(info["imported_by"]):
                        print(f"      -> {imp}")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print(f"  Total modules: {len(modules)}")
    print(f"  Internal dependencies: {len(graph['internal_edges'])}")
    print(f"  Circular dependencies: {len(graph['circular'])}")

    # Top external deps
    all_external = set()
    for deps in graph["external_deps"].values():
        all_external.update(deps)
    print(f"  External packages: {len(all_external)}")
    if all_external:
        print(f"    Top: {', '.join(sorted(all_external)[:10])}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate dependency graph for Python codebase"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to analyze (default: current)"
    )
    parser.add_argument(
        "--root",
        help="Root package name (e.g., 'kosmos')"
    )
    parser.add_argument(
        "--focus",
        help="Focus on modules matching this string"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
        sys.exit(1)

    graph = build_dependency_graph(args.directory, args.root)

    if args.json:
        # Clean up for JSON output
        output = {
            "modules": {
                k: {
                    "imports": v["imports"],
                    "imported_by": v["imported_by"]
                }
                for k, v in graph["modules"].items()
            },
            "layers": identify_layers(graph),
            "circular_dependencies": graph["circular"],
            "external_dependencies": graph["external_deps"],
            "summary": {
                "total_modules": len(graph["modules"]),
                "internal_edges": len(graph["internal_edges"]),
                "circular_count": len(graph["circular"])
            }
        }
        print(json.dumps(output, indent=2))
    else:
        print_text_graph(graph, args.focus)


if __name__ == "__main__":
    main()
