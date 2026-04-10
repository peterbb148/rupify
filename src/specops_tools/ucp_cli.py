"""CLI for deterministic SpecOps UCP calculation."""

from __future__ import annotations

import argparse
import json

from .structured_io import load_model
from .ucp import calculate_ucp, render_ucp_markdown


def main() -> int:
    """Run the UCP CLI.

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description="Calculate Use Case Points for a SpecOps model.")
    parser.add_argument("--model", required=True, help="Path to the model file.")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    args = parser.parse_args()

    model = load_model(args.model)
    results = calculate_ucp(model)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(render_ucp_markdown(model, results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

