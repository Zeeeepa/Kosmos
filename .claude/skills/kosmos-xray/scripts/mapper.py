#!/usr/bin/env python3
"""
Kosmos Codebase Mapper

Generates a directory structure map with token estimates.
Respects ignore patterns from configs and flags large files.

Usage:
    python mapper.py [directory] [--json] [--summary]

Examples:
    python mapper.py                    # Map current directory
    python mapper.py kosmos/            # Map specific directory
    python mapper.py --summary          # Show summary only
    python mapper.py --json             # Output as JSON
"""

import argparse
import fnmatch
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# Find the skill root directory (parent of scripts/)
SCRIPT_DIR = Path(__file__).parent
SKILL_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = SKILL_ROOT / "configs"


def load_ignore_patterns() -> Tuple[Set[str], Set[str], List[str]]:
    """Load ignore patterns from config file."""
    config_path = CONFIG_DIR / "ignore_patterns.json"

    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        return (
            set(config.get("directories", [])),
            set(config.get("extensions", [])),
            config.get("files", [])
        )

    # Sensible defaults if config missing
    return (
        {"__pycache__", ".git", "node_modules", ".venv", "artifacts"},
        {".pyc", ".log", ".pkl", ".jsonl"},
        []
    )


def estimate_tokens(filepath: str) -> int:
    """Estimate token count for a file (chars / 4)."""
    try:
        return os.path.getsize(filepath) // 4
    except (OSError, IOError):
        return 0


def format_tokens(tokens: int) -> str:
    """Format token count for display."""
    if tokens >= 1000:
        return f"{tokens / 1000:.1f}K"
    return str(tokens)


def get_size_tag(tokens: int) -> str:
    """Get warning tag for large files."""
    if tokens > 50000:
        return " [!!!HUGE]"
    elif tokens > 20000:
        return " [!LARGE]"
    elif tokens > 10000:
        return " [MEDIUM]"
    return ""


def should_ignore_dir(dirname: str, ignore_dirs: Set[str]) -> bool:
    """Check if directory should be ignored."""
    for pattern in ignore_dirs:
        if fnmatch.fnmatch(dirname, pattern):
            return True
    return dirname in ignore_dirs


def should_ignore_file(filename: str, ignore_exts: Set[str], ignore_files: List[str]) -> bool:
    """Check if file should be ignored."""
    ext = Path(filename).suffix
    if ext in ignore_exts:
        return True

    for pattern in ignore_files:
        if fnmatch.fnmatch(filename, pattern):
            return True

    return False


def map_directory(
    root_dir: str,
    ignore_dirs: Set[str],
    ignore_exts: Set[str],
    ignore_files: List[str]
) -> Dict:
    """
    Map directory structure with token estimates.

    Returns dict with structure:
    {
        "path": str,
        "total_tokens": int,
        "file_count": int,
        "tree": [...],
        "large_files": [...]
    }
    """
    root_path = Path(root_dir).resolve()
    tree_lines = []
    total_tokens = 0
    file_count = 0
    large_files = []

    tree_lines.append(f"ROOT: {root_path.name}/")

    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place
        dirs[:] = [d for d in sorted(dirs) if not should_ignore_dir(d, ignore_dirs)]

        rel_root = Path(root).relative_to(root_dir)
        level = len(rel_root.parts)
        indent = "    " * level

        if level > 0:
            tree_lines.append(f"{indent}{rel_root.name}/")

        subindent = "    " * (level + 1)

        for filename in sorted(files):
            if should_ignore_file(filename, ignore_exts, ignore_files):
                continue

            filepath = os.path.join(root, filename)
            tokens = estimate_tokens(filepath)
            total_tokens += tokens
            file_count += 1

            tag = get_size_tag(tokens)
            tree_lines.append(f"{subindent}{filename} ({format_tokens(tokens)} tok){tag}")

            if tokens > 10000:
                rel_path = str(Path(filepath).relative_to(root_dir))
                large_files.append({
                    "path": rel_path,
                    "tokens": tokens,
                    "formatted": format_tokens(tokens)
                })

    return {
        "path": str(root_path),
        "total_tokens": total_tokens,
        "file_count": file_count,
        "tree": tree_lines,
        "large_files": sorted(large_files, key=lambda x: x["tokens"], reverse=True)
    }


def print_tree(result: Dict, show_summary: bool = True):
    """Print the directory tree."""
    for line in result["tree"]:
        print(line)

    if show_summary:
        print()
        print("=" * 60)
        print(f"SUMMARY")
        print(f"  Total files: {result['file_count']}")
        print(f"  Total tokens: {format_tokens(result['total_tokens'])}")
        print(f"  Context budget: ~{result['total_tokens'] / 200000 * 100:.1f}% of 200K window")

        if result["large_files"]:
            print()
            print("LARGE FILES (>10K tokens) - Consider using skeleton.py instead:")
            for f in result["large_files"][:10]:  # Top 10
                print(f"  {f['formatted']:>8} tok  {f['path']}")


def print_summary_only(result: Dict):
    """Print summary without tree."""
    print(f"Directory: {result['path']}")
    print(f"Total files: {result['file_count']}")
    print(f"Total tokens: {format_tokens(result['total_tokens'])}")
    print(f"Context budget: ~{result['total_tokens'] / 200000 * 100:.1f}% of 200K window")

    if result["large_files"]:
        print()
        print("Large files (>10K tokens):")
        for f in result["large_files"]:
            print(f"  {f['formatted']:>8} tok  {f['path']}")


def main():
    parser = argparse.ArgumentParser(
        description="Map directory structure with token estimates"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to map (default: current directory)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary only, no tree"
    )

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
        sys.exit(1)

    ignore_dirs, ignore_exts, ignore_files = load_ignore_patterns()
    result = map_directory(args.directory, ignore_dirs, ignore_exts, ignore_files)

    if args.json:
        print(json.dumps(result, indent=2))
    elif args.summary:
        print_summary_only(result)
    else:
        print_tree(result)


if __name__ == "__main__":
    main()
