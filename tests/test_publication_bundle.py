"""Tests for stable specification publication bundles."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from rupify_tools.publication_bundle import (
    build_publication_bundle,
    create_bundle_archive,
    write_publication_bundle,
)
from tests.test_ucp import build_model


class PublicationBundleTests(unittest.TestCase):
    """Coverage for bundle publication and packaging."""

    def test_build_publication_bundle_uses_stable_layout_and_manifest(self) -> None:
        """The publication bundle should keep a stable layout and root manifest."""
        model = build_model()
        model["model_metadata"] = {
            "semantic_id": "rupify-model",
            "change_metadata": {"semantic_hash": "abc123", "change_source": "test_fixture"},
        }

        bundle = build_publication_bundle(model)

        self.assertIn(Path("bundle-manifest.json"), bundle)
        self.assertIn(Path("model") / "rupify-model.json", bundle)
        self.assertIn(Path("exports") / "speckify-planning-export.json", bundle)
        self.assertIn(Path("artifacts") / "formal" / "requirements-spec.md", bundle)
        self.assertIn(Path("artifacts") / "ucp" / "ucp-estimate.md", bundle)
        self.assertIn(Path("artifacts") / "mermaid" / "domain-model.mmd", bundle)
        self.assertIn(Path("artifacts") / "mermaid" / "state-model.mmd", bundle)

        manifest = json.loads(bundle[Path("bundle-manifest.json")])
        self.assertEqual(
            manifest["bundle_metadata"]["bundle_kind"],
            "rupify_specification_publication_bundle",
        )
        self.assertEqual(
            manifest["bundle_metadata"]["source_model_semantic_id"],
            "rupify-model",
        )
        self.assertEqual(
            manifest["layout"]["planning_export"],
            "exports/speckify-planning-export.json",
        )
        self.assertIn(
            "artifacts/formal/use-case-documents.md",
            manifest["layout"]["formal_artifacts"],
        )
        self.assertIn(
            "artifacts/mermaid/interaction-model.mmd",
            manifest["layout"]["mermaid_artifacts"],
        )
        self.assertEqual(manifest["summary"]["ucp_artifact_count"], 1)

    def test_write_publication_bundle_and_archive_create_expected_files(self) -> None:
        """The writer and archive helper should package the full bundle layout."""
        model = build_model()
        model["model_metadata"] = {
            "semantic_id": "rupify-model",
            "change_metadata": {"semantic_hash": "abc123"},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "published-spec"
            archive_path = Path(temp_dir) / "published-spec.zip"

            written_paths = write_publication_bundle(model, output_dir)
            create_bundle_archive(output_dir, archive_path)

            self.assertTrue((output_dir / "bundle-manifest.json").exists())
            self.assertTrue((output_dir / "model" / "rupify-model.json").exists())
            self.assertTrue(
                (output_dir / "artifacts" / "formal" / "system-document.md").exists()
            )
            self.assertTrue(
                (output_dir / "exports" / "speckify-planning-export.json").exists()
            )
            self.assertTrue(archive_path.exists())
            self.assertEqual(len(written_paths), 17)

            with ZipFile(archive_path) as handle:
                archive_names = set(handle.namelist())

            self.assertIn("bundle-manifest.json", archive_names)
            self.assertIn("model/rupify-model.json", archive_names)
            self.assertIn("artifacts/mermaid/deployment-model.mmd", archive_names)

    def test_cli_writes_bundle_and_optional_archive(self) -> None:
        """The CLI should write the full publication bundle and optional archive."""
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.json"
            output_dir = Path(temp_dir) / "bundle"
            archive_path = Path(temp_dir) / "bundle.zip"
            model = build_model()
            model["model_metadata"] = {
                "semantic_id": "rupify-model",
                "change_metadata": {"semantic_hash": "abc123"},
            }
            model_path.write_text(json.dumps(model), encoding="utf-8")

            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "rupify_tools.publication_bundle_cli",
                    "--model",
                    str(model_path),
                    "--output-dir",
                    str(output_dir),
                    "--archive",
                    str(archive_path),
                ],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn(str(output_dir / "bundle-manifest.json"), result.stdout)
            self.assertIn(str(archive_path), result.stdout)
            self.assertTrue((output_dir / "artifacts" / "formal" / "domain-model.md").exists())
            self.assertTrue(archive_path.exists())

    def test_checked_in_cmdb_v2_bundle_includes_planning_export_and_manifest(self) -> None:
        """The checked-in CMDB V2 bundle should preserve the Speckify handoff surface."""
        repo_root = Path(__file__).resolve().parents[1]
        example_dir = repo_root / "examples" / "it-systems-inventory-v2"

        manifest_path = example_dir / "bundle-manifest.json"
        planning_export_path = example_dir / "exports" / "speckify-planning-export.json"
        readme_path = example_dir / "README.md"

        self.assertTrue(manifest_path.exists())
        self.assertTrue(planning_export_path.exists())
        self.assertTrue((example_dir / "model" / "rupify-model.json").exists())
        self.assertTrue(
            (example_dir / "artifacts" / "formal" / "system-document.md").exists()
        )
        self.assertTrue(
            (example_dir / "artifacts" / "mermaid" / "domain-model.mmd").exists()
        )
        self.assertIn("Speckify Handoff Surface", readme_path.read_text(encoding="utf-8"))

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        planning_export = json.loads(planning_export_path.read_text(encoding="utf-8"))

        self.assertEqual(
            manifest["bundle_metadata"]["bundle_kind"],
            "rupify_specification_publication_bundle",
        )
        self.assertEqual(
            manifest["layout"]["planning_export"],
            "exports/speckify-planning-export.json",
        )
        self.assertEqual(planning_export["export_metadata"]["export_kind"], "speckify_planning_export")
        self.assertEqual(planning_export["summary"]["blocking_ambiguity_count"], 0)
