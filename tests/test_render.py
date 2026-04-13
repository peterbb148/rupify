"""Tests for rendering SpecOps artifacts."""

from __future__ import annotations

import unittest

from specops_tools.render import render_requirements_spec
from specops_tools.ucp import calculate_ucp, render_ucp_markdown

try:
    from tests.test_ucp import build_model
except ModuleNotFoundError:
    from test_ucp import build_model


class RenderTests(unittest.TestCase):
    """Coverage for rendering helpers."""

    def test_requirements_render_supports_structured_uncertainty_items(self) -> None:
        """Requirements rendering should preserve uncertainty metadata when present."""
        model = build_model()
        model["assumptions"] = [
            {
                "text": "Initial estimate assumes one delivery team.",
                "status": "assumed",
                "source": "interview round 2",
                "last_updated": "2026-04-13",
                "notes": "Team topology still needs confirmation.",
            }
        ]
        model["open_questions"] = [
            {
                "text": "Should partner merchants count as actors in V1?",
                "status": "unknown",
                "source": "portfolio workshop",
            }
        ]

        rendered = render_requirements_spec(model)

        self.assertIn("status: assumed", rendered)
        self.assertIn("source: interview round 2", rendered)
        self.assertIn("last updated: 2026-04-13", rendered)
        self.assertIn("notes: Team topology still needs confirmation.", rendered)
        self.assertIn("status: unknown", rendered)

    def test_ucp_render_supports_structured_uncertainty_items(self) -> None:
        """UCP rendering should preserve uncertainty metadata when present."""
        model = build_model()
        model["assumptions"] = [
            {
                "text": "Initial estimate assumes one delivery team.",
                "status": "assumed",
                "source": "interview round 2",
            }
        ]
        model["open_questions"] = [
            {
                "text": "Should partner merchants count as actors in V1?",
                "status": "unknown",
                "notes": "Could affect actor count and UCP.",
            }
        ]

        rendered = render_ucp_markdown(model, calculate_ucp(model))

        self.assertIn("status: assumed", rendered)
        self.assertIn("source: interview round 2", rendered)
        self.assertIn("status: unknown", rendered)
        self.assertIn("notes: Could affect actor count and UCP.", rendered)
