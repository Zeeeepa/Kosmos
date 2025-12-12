"""
Token estimation utilities for context budget management.

Provides rough token counts without requiring tokenizer libraries.
Uses the heuristic: ~4 characters per token for code.
"""

import os
from pathlib import Path
from typing import Dict, Optional


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for a string.

    Args:
        text: The text to estimate tokens for

    Returns:
        Estimated token count (chars / 4)
    """
    return len(text) // 4


def estimate_file_tokens(filepath: str) -> int:
    """
    Estimate token count for a file.

    Args:
        filepath: Path to the file

    Returns:
        Estimated token count, or 0 if file cannot be read
    """
    try:
        return os.path.getsize(filepath) // 4
    except (OSError, IOError):
        return 0


def categorize_size(tokens: int) -> str:
    """
    Categorize file size by token count.

    Args:
        tokens: Estimated token count

    Returns:
        Size category string
    """
    if tokens > 50000:
        return "[HUGE]"
    elif tokens > 20000:
        return "[LARGE]"
    elif tokens > 5000:
        return "[MEDIUM]"
    else:
        return ""


def get_directory_token_summary(
    directory: str,
    ignore_dirs: Optional[set] = None,
    ignore_exts: Optional[set] = None
) -> Dict[str, int]:
    """
    Get token counts for all files in a directory.

    Args:
        directory: Root directory to scan
        ignore_dirs: Directory names to skip
        ignore_exts: File extensions to skip

    Returns:
        Dict mapping file paths to token counts
    """
    ignore_dirs = ignore_dirs or set()
    ignore_exts = ignore_exts or set()

    results = {}

    for root, dirs, files in os.walk(directory):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in files:
            ext = Path(filename).suffix
            if ext in ignore_exts:
                continue

            filepath = os.path.join(root, filename)
            results[filepath] = estimate_file_tokens(filepath)

    return results


def format_token_count(tokens: int) -> str:
    """
    Format token count for display.

    Args:
        tokens: Token count

    Returns:
        Formatted string (e.g., "1.2K", "45K")
    """
    if tokens >= 1000:
        return f"{tokens / 1000:.1f}K"
    return str(tokens)
