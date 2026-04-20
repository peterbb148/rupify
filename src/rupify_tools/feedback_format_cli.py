"""CLI for normalizing the structured downstream feedback artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .feedback_format import normalize_feedback_artifact
from .structured_io import load_model, write_text


def main() -> int:
    """Normalize a Speckify feedback payload into the strict feedback contract."""
    parser = argparse.ArgumentParser(
        description="Normalize the structured round-trip feedback format for downstream corrections."
    )
    parser.add_argument("--input", required=True, help="Path to the raw feedback JSON/YAML file.")
    parser.add_argument("--output", required=True, help="Path where the normalized feedback JSON should be written.")
    args = parser.parse_args()

    payload = load_model(args.input)
    normalized = normalize_feedback_artifact(payload)
    output_path = Path(args.output)
    write_text(output_path, json.dumps(normalized, indent=2, sort_keys=True))
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
