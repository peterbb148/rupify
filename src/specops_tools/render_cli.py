"""CLI for rendering SpecOps artifacts from a canonical model."""

from __future__ import annotations

import argparse
from pathlib import Path

from .render import render_all
from .structured_io import load_model, write_text


def main() -> int:
    """Run the renderer CLI.

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description="Render SpecOps Markdown artifacts from a model.")
    parser.add_argument("--model", required=True, help="Path to the model file.")
    parser.add_argument("--output-dir", required=True, help="Output directory for rendered files.")
    args = parser.parse_args()

    model = load_model(args.model)
    outputs = render_all(model)

    output_dir = Path(args.output_dir)
    for filename, content in outputs.items():
        write_text(output_dir / filename, content)
        print(output_dir / filename)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

