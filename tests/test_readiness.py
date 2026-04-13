"""Tests for readiness and staleness reporting."""

from __future__ import annotations

import unittest

from specops_tools.readiness import evaluate_readiness, identify_stale_artifacts


class ReadinessTests(unittest.TestCase):
    """Coverage for interview-state readiness helpers."""

    def test_evaluate_readiness_reports_partial_and_ready_views(self) -> None:
        """Readiness should distinguish complete, partial, and blocked views."""
        readiness = evaluate_readiness(
            [
                {"round": 1, "responses": []},
                {"round": 3, "responses": []},
                {"round": 4, "responses": []},
                {"round": 5, "responses": []},
                {"round": 6, "responses": []},
                {"round": 7, "responses": []},
                {"round": 8, "responses": []},
            ]
        )

        self.assertEqual(readiness["discovery"], "partial")
        self.assertEqual(readiness["use_case"], "ready")
        self.assertEqual(readiness["logical"], "ready")
        self.assertEqual(readiness["process"], "ready")
        self.assertEqual(readiness["architecture"], "ready")
        self.assertEqual(readiness["ucp"], "partial")

    def test_identify_stale_artifacts_maps_round_updates_to_outputs(self) -> None:
        """Updated rounds should mark only dependent artifacts stale."""
        stale = identify_stale_artifacts(
            [
                {"round": 2, "responses": []},
                {"round": 9, "responses": []},
            ]
        )

        self.assertEqual(
            stale,
            ["requirements-spec.md", "ucp-estimate.md"],
        )
