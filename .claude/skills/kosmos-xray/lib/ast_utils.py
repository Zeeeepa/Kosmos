"""
AST utilities for Python code analysis.

Extracts structural information (classes, methods, signatures) without
loading full implementation details, achieving ~95% token reduction.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def get_skeleton(filepath: str, include_private: bool = False) -> str:
    """
    Extract the skeleton (interface) of a Python file using AST.

    Shows classes, methods, and function signatures without implementations.

    Args:
        filepath: Path to Python file
        include_private: Include _private methods (default: False)

    Returns:
        Skeleton representation of the file
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception as e:
        return f"# Error parsing {filepath}: {e}"

    lines = [f"# SKELETON: {filepath}"]
    lines.append(f"# Token savings: ~{len(source) // 4} -> ~{_estimate_skeleton_tokens(tree)}")
    lines.append("")

    # Process module-level docstring
    if (doc := ast.get_docstring(tree)):
        summary = doc.strip().splitlines()[0]
        lines.append(f'"""{summary}..."""')
        lines.append("")

    # Process top-level nodes
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            _process_class(node, lines, 0, include_private)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if include_private or not node.name.startswith('_'):
                _process_function(node, lines, 0)

    return "\n".join(lines)


def _process_class(node: ast.ClassDef, lines: List[str], indent: int, include_private: bool):
    """Process a class definition."""
    prefix = "    " * indent

    # Build class signature
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(f"{_get_attr_name(base)}")

    base_str = f"({', '.join(bases)})" if bases else ""
    lines.append(f"{prefix}class {node.name}{base_str}:")

    # Add docstring
    if (doc := ast.get_docstring(node)):
        summary = doc.strip().splitlines()[0]
        lines.append(f'{prefix}    """{summary}..."""')

    # Process methods
    has_methods = False
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if include_private or not child.name.startswith('_') or child.name in ('__init__', '__call__', '__enter__', '__exit__'):
                _process_function(child, lines, indent + 1)
                has_methods = True

    if not has_methods:
        lines.append(f"{prefix}    pass")

    lines.append("")


def _process_function(node, lines: List[str], indent: int):
    """Process a function/method definition."""
    prefix = "    " * indent

    is_async = "async " if isinstance(node, ast.AsyncFunctionDef) else ""

    # Build argument list
    args = []
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {_get_annotation(arg.annotation)}"
        args.append(arg_str)

    # Handle *args and **kwargs
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")

    # Return annotation
    return_annotation = ""
    if node.returns:
        return_annotation = f" -> {_get_annotation(node.returns)}"

    lines.append(f"{prefix}{is_async}def {node.name}({', '.join(args)}){return_annotation}: ...")

    # Add docstring summary
    if (doc := ast.get_docstring(node)):
        summary = doc.strip().splitlines()[0]
        lines.append(f'{prefix}    """{summary}..."""')


def _get_annotation(node) -> str:
    """Extract type annotation as string."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):
        return repr(node.value)
    elif isinstance(node, ast.Subscript):
        value = _get_annotation(node.value)
        slice_val = _get_annotation(node.slice)
        return f"{value}[{slice_val}]"
    elif isinstance(node, ast.Tuple):
        elts = ", ".join(_get_annotation(e) for e in node.elts)
        return elts
    elif isinstance(node, ast.Attribute):
        return _get_attr_name(node)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        # Union type (X | Y)
        left = _get_annotation(node.left)
        right = _get_annotation(node.right)
        return f"{left} | {right}"
    return "..."


def _get_attr_name(node: ast.Attribute) -> str:
    """Get full dotted name from Attribute node."""
    parts = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def _estimate_skeleton_tokens(tree: ast.AST) -> int:
    """Estimate tokens in skeleton output."""
    # Rough estimate based on node count
    count = sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)))
    return count * 50  # ~50 tokens per definition


def parse_imports(filepath: str) -> Tuple[List[str], List[str]]:
    """
    Parse imports from a Python file.

    Args:
        filepath: Path to Python file

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


def get_class_hierarchy(filepath: str) -> Dict[str, List[str]]:
    """
    Extract class inheritance hierarchy from a Python file.

    Args:
        filepath: Path to Python file

    Returns:
        Dict mapping class names to their base classes
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
    except Exception:
        return {}

    hierarchy = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(_get_attr_name(base))
            hierarchy[node.name] = bases

    return hierarchy
