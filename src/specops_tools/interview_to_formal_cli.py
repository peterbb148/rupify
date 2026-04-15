"""CLI for generating formal SpecOps artifacts directly from an interview fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .discovery import normalize_replay_to_model
from .interview import replay_session, replay_session_with_updates
from .render import render_artifact_family
from .structured_io import write_text


def _write_model(path: Path, model: dict[str, object]) -> None:
    """Write the normalized canonical model as JSON."""
    write_text(path, json.dumps(model, indent=2, sort_keys=True))


def main() -> int:
    """Run the interview-to-formal-artifacts pipeline CLI.

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(
        description="Replay an interview fixture and render the formal SpecOps artifacts."
    )
    parser.add_argument("--input", required=True, help="Path to the interview fixture JSON file.")
    parser.add_argument(
        "--updates",
        help="Optional path to a JSON file containing targeted round updates.",
    )
    parser.add_argument("--output-dir", required=True, help="Output directory for rendered files.")
    parser.add_argument(
        "--write-model",
        help="Optional path where the normalized canonical model should be written.",
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        fixture = json.load(handle)

    rounds = fixture.get("rounds", [])
    if args.updates:
        with open(args.updates, "r", encoding="utf-8") as handle:
            update_fixture = json.load(handle)
        replay = replay_session_with_updates(rounds, update_fixture.get("rounds", []))
    else:
        replay = replay_session(rounds)

    model = normalize_replay_to_model(replay)
    outputs = render_artifact_family(model, "formal")

    output_dir = Path(args.output_dir)
    for filename, content in outputs.items():
        write_text(output_dir / filename, content)
        print(output_dir / filename)

    if args.write_model:
        _write_model(Path(args.write_model), model)
        print(Path(args.write_model))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
