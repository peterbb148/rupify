"""Specification publication bundle generation for Rupify."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from .planning_export import build_planning_export
from .render import render_artifact_family
from .structured_io import write_text


BUNDLE_MANIFEST_FILENAME = "bundle-manifest.json"
MODEL_OUTPUT_PATH = Path("model") / "rupify-model.json"
PLANNING_EXPORT_OUTPUT_PATH = Path("exports") / "speckify-planning-export.json"
FORMAL_OUTPUT_DIR = Path("artifacts") / "formal"
UCP_OUTPUT_DIR = Path("artifacts") / "ucp"
MERMAID_OUTPUT_DIR = Path("artifacts") / "mermaid"
MERMAID_FAMILIES: tuple[str, ...] = (
    "domain-mermaid",
    "interaction-mermaid",
    "deployment-mermaid",
    "state-mermaid",
)


def _json_text(payload: dict[str, Any]) -> str:
    """Return stable JSON text for one bundle payload."""
    return json.dumps(payload, indent=2, sort_keys=True)


def _relative_paths(paths: list[Path]) -> list[str]:
    """Return sorted bundle-relative path strings."""
    return sorted(str(path).replace("\\", "/") for path in paths)


def _artifact_paths_for_family(
    artifact_family: str,
    output_dir: Path,
    model: dict[str, Any],
) -> dict[Path, str]:
    """Render one artifact family into bundle-relative paths."""
    rendered = render_artifact_family(model, artifact_family)
    return {output_dir / filename: content for filename, content in rendered.items()}


def _build_manifest(
    model: dict[str, Any],
    bundle_files: dict[Path, str],
) -> dict[str, Any]:
    """Build the stable publication bundle manifest."""
    model_metadata = model.get("model_metadata", {})
    artifact_paths = [
        path for path in bundle_files if path.parts and path.parts[0] == "artifacts"
    ]
    formal_paths = [
        path for path in artifact_paths if path.parts[:2] == ("artifacts", "formal")
    ]
    mermaid_paths = [
        path for path in artifact_paths if path.parts[:2] == ("artifacts", "mermaid")
    ]
    ucp_paths = [path for path in artifact_paths if path.parts[:2] == ("artifacts", "ucp")]

    return {
        "bundle_metadata": {
            "schema_version": 1,
            "bundle_kind": "rupify_specification_publication_bundle",
            "source_model_semantic_id": model_metadata.get("semantic_id", ""),
            "source_model_change_metadata": model_metadata.get("change_metadata", {}),
            "generated_artifact_families": [
                "formal",
                "ucp",
                *MERMAID_FAMILIES,
                "speckify-planning-export",
            ],
        },
        "layout": {
            "model": str(MODEL_OUTPUT_PATH),
            "formal_artifacts": _relative_paths(formal_paths),
            "ucp_artifacts": _relative_paths(ucp_paths),
            "mermaid_artifacts": _relative_paths(mermaid_paths),
            "planning_export": str(PLANNING_EXPORT_OUTPUT_PATH),
        },
        "summary": {
            "file_count": len(bundle_files) + 1,
            "formal_artifact_count": len(formal_paths),
            "ucp_artifact_count": len(ucp_paths),
            "mermaid_artifact_count": len(mermaid_paths),
        },
    }


def build_publication_bundle(model: dict[str, Any]) -> dict[Path, str]:
    """Build the stable publication bundle for one canonical model."""
    bundle_files: dict[Path, str] = {
        MODEL_OUTPUT_PATH: _json_text(model),
        PLANNING_EXPORT_OUTPUT_PATH: _json_text(build_planning_export(model)),
    }
    bundle_files.update(_artifact_paths_for_family("formal", FORMAL_OUTPUT_DIR, model))
    bundle_files.update(_artifact_paths_for_family("ucp", UCP_OUTPUT_DIR, model))
    for family in MERMAID_FAMILIES:
        bundle_files.update(_artifact_paths_for_family(family, MERMAID_OUTPUT_DIR, model))

    bundle_files[Path(BUNDLE_MANIFEST_FILENAME)] = _json_text(
        _build_manifest(model, bundle_files)
    )
    return dict(sorted(bundle_files.items(), key=lambda item: str(item[0])))


def write_publication_bundle(
    model: dict[str, Any],
    output_dir: str | Path,
) -> list[Path]:
    """Write the publication bundle to one output directory."""
    root = Path(output_dir)
    written_paths = []
    for relative_path, content in build_publication_bundle(model).items():
        output_path = root / relative_path
        write_text(output_path, content)
        written_paths.append(output_path)
    return written_paths


def create_bundle_archive(output_dir: str | Path, archive_path: str | Path) -> Path:
    """Create a zip archive from a previously written publication bundle."""
    root = Path(output_dir)
    destination = Path(archive_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as handle:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                handle.write(path, arcname=path.relative_to(root))
    return destination
