"""CLI for writing a stable Rupify publication bundle."""

from __future__ import annotations

import argparse

from .publication_bundle import create_bundle_archive, write_publication_bundle
from .structured_io import load_model


def main() -> int:
    """Build the stable publication bundle from a canonical model."""
    parser = argparse.ArgumentParser(
        description="Build a stable publication bundle from a normalized Rupify model."
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Path to the normalized Rupify model JSON/YAML.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the bundle should be written.",
    )
    parser.add_argument(
        "--archive",
        help="Optional path where a zip archive of the written bundle should be created.",
    )
    args = parser.parse_args()

    model = load_model(args.model)
    for path in write_publication_bundle(model, args.output_dir):
        print(path)

    if args.archive:
        print(create_bundle_archive(args.output_dir, args.archive))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
