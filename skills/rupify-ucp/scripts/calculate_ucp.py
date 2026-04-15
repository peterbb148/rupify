#!/usr/bin/env python3
"""Wrapper for the repository-level Rupify UCP calculator."""

from pathlib import Path
import sys


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root / "src"))
    from rupify_tools.ucp_cli import main as ucp_main

    return ucp_main()


if __name__ == "__main__":
    raise SystemExit(main())

