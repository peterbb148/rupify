"""CLI for replaying a SpecOps interview session from a fixture."""

from __future__ import annotations

import argparse
import json

from .interview import replay_session, to_json


def main() -> int:
    """Run the interview replay CLI.

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description="Replay a SpecOps interview session.")
    parser.add_argument("--input", required=True, help="Path to the replay fixture JSON file.")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        fixture = json.load(handle)

    rounds = fixture.get("rounds", [])
    print(to_json(replay_session(rounds)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

