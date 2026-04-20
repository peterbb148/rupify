"""Tests for the structured round-trip feedback contract."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from rupify_tools.feedback_format import normalize_feedback_artifact


class FeedbackFormatTests(unittest.TestCase):
    """Coverage for the downstream feedback artifact contract."""

    def test_normalize_feedback_artifact_preserves_upstream_links_and_proposals(self) -> None:
        """Normalization should preserve upstream semantic ids, hashes, and proposal structure."""
        payload = {
            "feedback_metadata": {
                "source_model_semantic_id": "rupify-model",
                "source_model_change_hash": "modelhash123",
                "source_planning_export_semantic_id": "rupify-model",
                "source_planning_export_change_hash": "exporthash123",
                "emitted_by": "speckify",
                "emitted_at": "2026-04-20T10:15:00Z",
            },
            "feedback_items": [
                {
                    "category": "clarify",
                    "title": "Clarify owner validation rule",
                    "description": "Temporary owner handling is ambiguous downstream.",
                    "target_semantic_ids": ["domain-invariant-1"],
                    "target_change_hashes": ["invarhash123"],
                    "target_families": ["domain_invariants"],
                    "blocking_for_downstream": True,
                    "downstream_evidence": ["Task graph diverged on owner validation."],
                    "proposed_changes": [
                        {
                            "field_path": "logical_view.domain_invariant_objects[0].description",
                            "value": "A system must have a permanent owner before approval.",
                            "rationale": "Downstream planning needs one rule.",
                        }
                    ],
                    "requested_action": "Clarify the invariant upstream.",
                }
            ],
        }

        normalized = normalize_feedback_artifact(payload)

        self.assertEqual(normalized["feedback_metadata"]["feedback_kind"], "speckify_feedback")
        self.assertEqual(normalized["feedback_metadata"]["proposal_only"], True)
        self.assertEqual(normalized["summary"]["blocking_item_count"], 1)
        self.assertEqual(normalized["summary"]["categories"], {"clarify": 1})
        self.assertEqual(normalized["summary"]["target_semantic_ids"], ["domain-invariant-1"])
        self.assertEqual(normalized["feedback_items"][0]["target_change_hashes"], ["invarhash123"])
        self.assertEqual(normalized["feedback_items"][0]["proposal_status"], "proposed")
        self.assertEqual(
            normalized["feedback_items"][0]["proposed_changes"][0]["operation"],
            "revise",
        )

    def test_normalize_feedback_artifact_rejects_unknown_category(self) -> None:
        """Unsupported categories should fail clearly instead of degrading silently."""
        with self.assertRaisesRegex(ValueError, "Unsupported feedback category"):
            normalize_feedback_artifact(
                {
                    "feedback_items": [
                        {
                            "category": "invent_new_category",
                            "title": "Bad category",
                            "description": "Unsupported.",
                            "target_semantic_ids": ["uc-redeem"],
                        }
                    ]
                }
            )

    def test_cli_writes_normalized_feedback_json(self) -> None:
        """The feedback CLI should normalize a fixture and write JSON output."""
        repo_root = Path(__file__).resolve().parents[1]
        fixture_path = repo_root / "tests" / "fixtures" / "speckify_feedback_example.json"
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "normalized-feedback.json"
            completed = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "rupify_tools.feedback_format_cli",
                    "--input",
                    str(fixture_path),
                    "--output",
                    str(output_path),
                ],
                text=True,
                capture_output=True,
                check=True,
                cwd=repo_root,
            )

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feedback_metadata"]["feedback_kind"], "speckify_feedback")
            self.assertEqual(payload["summary"]["feedback_item_count"], 2)
            self.assertEqual(payload["summary"]["blocking_item_count"], 1)
            self.assertIn("domain-invariant-1", payload["summary"]["target_semantic_ids"])
            self.assertIn(str(output_path), completed.stdout)


if __name__ == "__main__":
    unittest.main()
