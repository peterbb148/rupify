"""CLI for writing the machine-oriented downstream planning export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .planning_export import build_planning_export
from .structured_io import load_model, write_text


def main() -> int:
    """Generate the downstream planning export from a normalized Rupify model."""
    parser = argparse.ArgumentParser(
        description="Build the machine-oriented downstream planning export for Speckify."
    )
    parser.add_argument("--model", required=True, help="Path to the normalized Rupify model JSON/YAML.")
    parser.add_argument("--output", required=True, help="Path where the export JSON should be written.")
    args = parser.parse_args()

    model = load_model(args.model)
    export = build_planning_export(model)
    output_path = Path(args.output)
    write_text(output_path, json.dumps(export, indent=2, sort_keys=True))
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
