"""CLI for replaying a Rupify interview session from a fixture."""

from __future__ import annotations

import argparse
import json

from .interview import replay_session, replay_session_with_updates, to_json


def main() -> int:
    """Run the interview replay CLI.

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description="Replay a Rupify interview session.")
    parser.add_argument("--input", required=True, help="Path to the replay fixture JSON file.")
    parser.add_argument(
        "--updates",
        help="Optional path to a JSON file containing targeted round updates.",
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        fixture = json.load(handle)

    rounds = fixture.get("rounds", [])
    if args.updates:
        with open(args.updates, "r", encoding="utf-8") as handle:
            update_fixture = json.load(handle)
        updates = update_fixture.get("rounds", [])
        print(to_json(replay_session_with_updates(rounds, updates)))
    else:
        print(to_json(replay_session(rounds)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
