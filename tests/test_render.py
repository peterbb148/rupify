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

    def test_requirements_render_includes_extended_view_sections(self) -> None:
        """Requirements rendering should include logical, process, and architecture sections when present."""
        model = build_model()
        model["logical_view"] = {
            "domain_entities": ["Member", "Reward"],
            "relationships": ["A Member can redeem many Rewards."],
            "business_rules": ["A Reward requires sufficient points."],
        }
        model["process_view"] = {
            "state_entities": ["Redemption request"],
            "states_and_transitions": ["Requested -> Approved -> Fulfilled"],
            "triggers_and_approvals": ["Approval is required for manual fulfillment."],
        }
        model["architecture_view"] = {
            "components_and_services": ["Member app", "Rewards API"],
            "interfaces_and_integrations": ["Member app calls Rewards API."],
            "runtime_boundaries": ["Rewards API runs as a separate service."],
        }

        rendered = render_requirements_spec(model)

        self.assertIn("## Logical View", rendered)
        self.assertIn("Member", rendered)
        self.assertIn("## Process View", rendered)
        self.assertIn("Requested -> Approved -> Fulfilled", rendered)
        self.assertIn("## Architecture View", rendered)
        self.assertIn("Rewards API runs as a separate service.", rendered)

    def test_use_case_render_includes_process_and_architecture_sections(self) -> None:
        """Use-case rendering should include relevant process and architecture sections when present."""
        from specops_tools.render import render_use_case_model

        model = build_model()
        model["process_view"] = {
            "states_and_transitions": ["Requested -> Approved -> Fulfilled"],
            "triggers_and_approvals": ["Approval is required for manual fulfillment."],
        }
        model["architecture_view"] = {
            "interfaces_and_integrations": ["Member app calls Rewards API."],
        }

        rendered = render_use_case_model(model)

        self.assertIn("## States and Transitions", rendered)
        self.assertIn("Requested -> Approved -> Fulfilled", rendered)
        self.assertIn("## Interfaces and Integrations", rendered)
        self.assertIn("Member app calls Rewards API.", rendered)

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
