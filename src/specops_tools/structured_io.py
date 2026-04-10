"""Structured model loading for SpecOps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_model(path: str | Path) -> dict[str, Any]:
    """Load a SpecOps model from JSON or YAML.

    Args:
        path: Path to the model file.

    Returns:
        Parsed model data.

    Raises:
        RuntimeError: If YAML support is requested without the optional dependency.
        ValueError: If the file extension is unsupported.
    """
    model_path = Path(path)
    suffix = model_path.suffix.lower()
    raw = model_path.read_text()

    if suffix == ".json":
        return json.loads(raw)

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "YAML support is not installed. Run `uv sync --extra yaml` before using a YAML model."
            ) from exc
        return yaml.safe_load(raw)

    raise ValueError(f"Unsupported model format: {model_path.suffix}")


def write_text(path: str | Path, content: str) -> None:
    """Write UTF-8 text to a file.

    Args:
        path: Destination path.
        content: Content to write.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)

