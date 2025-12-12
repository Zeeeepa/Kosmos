#!/usr/bin/env python3
"""
Kosmos Code Skeleton Extractor

Extracts Python file interfaces (classes, methods, signatures) via AST.
Achieves ~95% token reduction compared to reading full source.

Usage:
    python skeleton.py <file_or_directory> [options]

Examples:
    python skeleton.py kosmos/workflow/research_loop.py
    python skeleton.py kosmos/agents/
    python skeleton.py kosmos/ --pattern "**/base*.py"
    python skeleton.py kosmos/ --priority critical
"""

import argparse
import ast
import fnmatch
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# Find the skill root directory
SCRIPT_DIR = Path(__file__).parent
SKILL_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = SKILL_ROOT / "configs"


def load_priority_patterns() -> Dict:
    """Load priority patterns from config."""
    config_path = CONFIG_DIR / "priority_modules.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def load_ignore_patterns() -> Tuple[Set[str], Set[str], List[str]]:
    """Load ignore patterns from config."""
    config_path = CONFIG_DIR / "ignore_patterns.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        return (
            set(config.get("directories", [])),
            set(config.get("extensions", [])),
            config.get("files", [])
        )
    return ({"__pycache__", ".git"}, {".pyc"}, [])


def estimate_tokens(text: str) -> int:
    """Estimate token count."""
    return len(text) // 4


def get_skeleton(filepath: str, include_private: bool = False) -> Tuple[str, int, int]:
    """
    Extract skeleton from a Python file.

    Returns:
        Tuple of (skeleton_text, original_tokens, skeleton_tokens)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
    except SyntaxError as e:
        return f"# Syntax error in {filepath}: {e}", 0, 0
    except Exception as e:
        return f"# Error reading {filepath}: {e}", 0, 0

    original_tokens = estimate_tokens(source)
    lines = []

    # Module docstring
    if (doc := ast.get_docstring(tree)):
        summary = doc.strip().splitlines()[0][:100]
        lines.append(f'"""{summary}..."""')
        lines.append("")

    # Process top-level definitions
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            process_class(node, lines, 0, include_private)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if include_private or not node.name.startswith('_'):
                process_function(node, lines, 0)

    skeleton = "\n".join(lines)
    skeleton_tokens = estimate_tokens(skeleton)

    return skeleton, original_tokens, skeleton_tokens


def process_class(node: ast.ClassDef, lines: List[str], indent: int, include_private: bool):
    """Process a class definition."""
    prefix = "    " * indent

    # Class signature with bases
    bases = []
    for base in node.bases:
        bases.append(get_name(base))
    base_str = f"({', '.join(bases)})" if bases else ""

    lines.append(f"{prefix}class {node.name}{base_str}:")

    # Docstring
    if (doc := ast.get_docstring(node)):
        summary = doc.strip().splitlines()[0][:100]
        lines.append(f'{prefix}    """{summary}..."""')

    # Methods
    has_content = False
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Include dunders and public methods
            if (include_private or
                not child.name.startswith('_') or
                child.name.startswith('__') and child.name.endswith('__')):
                process_function(child, lines, indent + 1)
                has_content = True
        elif isinstance(child, ast.ClassDef):
            # Nested class
            process_class(child, lines, indent + 1, include_private)
            has_content = True

    if not has_content:
        lines.append(f"{prefix}    pass")

    lines.append("")


def process_function(node, lines: List[str], indent: int):
    """Process a function definition."""
    prefix = "    " * indent

    is_async = "async " if isinstance(node, ast.AsyncFunctionDef) else ""

    # Build argument list
    args = []
    defaults_offset = len(node.args.args) - len(node.args.defaults)

    for i, arg in enumerate(node.args.args):
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {get_annotation(arg.annotation)}"

        # Default value
        default_idx = i - defaults_offset
        if default_idx >= 0 and default_idx < len(node.args.defaults):
            default = node.args.defaults[default_idx]
            arg_str += f" = {get_default_repr(default)}"

        args.append(arg_str)

    # *args
    if node.args.vararg:
        vararg = f"*{node.args.vararg.arg}"
        if node.args.vararg.annotation:
            vararg += f": {get_annotation(node.args.vararg.annotation)}"
        args.append(vararg)

    # **kwargs
    if node.args.kwarg:
        kwarg = f"**{node.args.kwarg.arg}"
        if node.args.kwarg.annotation:
            kwarg += f": {get_annotation(node.args.kwarg.annotation)}"
        args.append(kwarg)

    # Return annotation
    ret = ""
    if node.returns:
        ret = f" -> {get_annotation(node.returns)}"

    lines.append(f"{prefix}{is_async}def {node.name}({', '.join(args)}){ret}: ...")

    # Docstring summary
    if (doc := ast.get_docstring(node)):
        summary = doc.strip().splitlines()[0][:80]
        lines.append(f'{prefix}    """{summary}..."""')


def get_name(node) -> str:
    """Get name from various node types."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    elif isinstance(node, ast.Subscript):
        return f"{get_name(node.value)}[{get_annotation(node.slice)}]"
    return "..."


def get_annotation(node) -> str:
    """Get type annotation string."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):
        if node.value is None:
            return "None"
        return repr(node.value)
    elif isinstance(node, ast.Subscript):
        value = get_name(node.value)
        slice_val = get_annotation(node.slice)
        return f"{value}[{slice_val}]"
    elif isinstance(node, ast.Tuple):
        return ", ".join(get_annotation(e) for e in node.elts)
    elif isinstance(node, ast.Attribute):
        return get_name(node)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return f"{get_annotation(node.left)} | {get_annotation(node.right)}"
    elif isinstance(node, ast.List):
        return "[" + ", ".join(get_annotation(e) for e in node.elts) + "]"
    return "..."


def get_default_repr(node) -> str:
    """Get string representation of default value."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str) and len(node.value) > 20:
            return '"..."'
        return repr(node.value)
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, (ast.List, ast.Tuple, ast.Dict)):
        return "..."
    elif isinstance(node, ast.Call):
        return f"{get_name(node.func)}(...)"
    return "..."


def find_python_files(
    directory: str,
    pattern: Optional[str] = None,
    priority: Optional[str] = None
) -> List[str]:
    """Find Python files matching criteria."""
    ignore_dirs, ignore_exts, _ = load_ignore_patterns()
    priority_config = load_priority_patterns()

    files = []

    # Get glob patterns for priority level
    glob_patterns = []
    if priority and priority_config.get("priority_patterns", {}).get(priority):
        glob_patterns = priority_config["priority_patterns"][priority].get("patterns", [])

    for root, dirs, filenames in os.walk(directory):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, directory)

            # Check custom pattern
            if pattern and not fnmatch.fnmatch(rel_path, pattern):
                continue

            # Check priority patterns
            if glob_patterns:
                if not any(fnmatch.fnmatch(rel_path, p.lstrip('**/')) for p in glob_patterns):
                    continue

            files.append(filepath)

    return sorted(files)


def main():
    parser = argparse.ArgumentParser(
        description="Extract Python file skeletons via AST"
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyze"
    )
    parser.add_argument(
        "--pattern",
        help="Glob pattern to filter files (e.g., '**/base*.py')"
    )
    parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low"],
        help="Filter by priority level from config"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Include private methods (starting with _)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    if os.path.isfile(args.path):
        files = [args.path]
    elif os.path.isdir(args.path):
        files = find_python_files(args.path, args.pattern, args.priority)
    else:
        print(f"Error: '{args.path}' not found", file=sys.stderr)
        sys.exit(1)

    if not files:
        print("No Python files found matching criteria", file=sys.stderr)
        sys.exit(1)

    results = []
    total_original = 0
    total_skeleton = 0

    for filepath in files:
        skeleton, orig_tok, skel_tok = get_skeleton(filepath, args.private)
        total_original += orig_tok
        total_skeleton += skel_tok

        if args.json:
            results.append({
                "file": filepath,
                "original_tokens": orig_tok,
                "skeleton_tokens": skel_tok,
                "reduction": f"{(1 - skel_tok/orig_tok)*100:.1f}%" if orig_tok > 0 else "N/A",
                "skeleton": skeleton
            })
        else:
            print(f"# {'=' * 60}")
            print(f"# FILE: {filepath}")
            print(f"# Tokens: {orig_tok} -> {skel_tok} ({(1 - skel_tok/orig_tok)*100:.1f}% reduction)" if orig_tok > 0 else "# Tokens: N/A")
            print(f"# {'=' * 60}")
            print(skeleton)
            print()

    if args.json:
        output = {
            "files": results,
            "summary": {
                "file_count": len(files),
                "total_original_tokens": total_original,
                "total_skeleton_tokens": total_skeleton,
                "overall_reduction": f"{(1 - total_skeleton/total_original)*100:.1f}%" if total_original > 0 else "N/A"
            }
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print("SUMMARY")
        print(f"  Files processed: {len(files)}")
        print(f"  Original tokens: {total_original}")
        print(f"  Skeleton tokens: {total_skeleton}")
        if total_original > 0:
            print(f"  Reduction: {(1 - total_skeleton/total_original)*100:.1f}%")


if __name__ == "__main__":
    main()
