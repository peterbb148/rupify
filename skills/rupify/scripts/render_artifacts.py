#!/usr/bin/env python3
"""Wrapper for the repository-level Rupify renderer."""

from pathlib import Path
import sys


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root / "src"))
    from rupify_tools.render_cli import main as render_main

    return render_main()


if __name__ == "__main__":
    raise SystemExit(main())

