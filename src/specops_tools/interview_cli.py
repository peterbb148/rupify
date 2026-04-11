"""CLI for processing one SpecOps interview round."""

from __future__ import annotations

import argparse
import sys

from .interview import process_round, to_json


def main() -> int:
    """Run the interview round CLI.

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description="Process one SpecOps interview round.")
    parser.add_argument("--round", type=int, required=True, help="Interview round number.")
    parser.add_argument(
        "--input",
        help="Optional path to the answer text. If omitted, stdin is used.",
    )
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as handle:
            answer_text = handle.read()
    else:
        answer_text = sys.stdin.read()

    print(to_json(process_round(args.round, answer_text)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

