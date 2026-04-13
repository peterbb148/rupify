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
            "domain_entity_objects": [
                {
                    "id": "entity-member",
                    "name": "Member",
                    "trace": {"source_round": 5, "source_key": "domain_entities"},
                },
                {
                    "id": "entity-reward",
                    "name": "Reward",
                    "trace": {"source_round": 5, "source_key": "domain_entities"},
                },
            ],
            "relationships": ["A Member can redeem many Rewards."],
            "relationship_objects": [
                {
                    "id": "relationship-1",
                    "text": "A Member can redeem many Rewards.",
                    "trace": {"source_round": 5, "source_key": "relationships"},
                },
            ],
            "business_rules": ["A Reward requires sufficient points."],
            "business_rule_objects": [
                {
                    "id": "business-rule-1",
                    "text": "A Reward requires sufficient points.",
                    "trace": {"source_round": 5, "source_key": "business_rules"},
                },
            ],
        }
        model["process_view"] = {
            "state_entities": ["Redemption request"],
            "state_entity_objects": [
                {
                    "id": "state-entity-redemption-request",
                    "name": "Redemption request",
                    "trace": {"source_round": 6, "source_key": "state_entities"},
                },
            ],
            "states_and_transitions": ["Requested -> Approved -> Fulfilled"],
            "state_transition_objects": [
                {
                    "id": "state-transition-1",
                    "text": "Requested -> Approved -> Fulfilled",
                    "trace": {"source_round": 6, "source_key": "states_and_transitions"},
                },
            ],
            "triggers_and_approvals": ["Approval is required for manual fulfillment."],
            "trigger_objects": [
                {
                    "id": "trigger-1",
                    "text": "Approval is required for manual fulfillment.",
                    "trace": {"source_round": 6, "source_key": "triggers_and_approvals"},
                },
            ],
        }
        model["architecture_view"] = {
            "components_and_services": ["Member app", "Rewards API"],
            "component_objects": [
                {
                    "id": "component-member-app",
                    "name": "Member app",
                    "trace": {"source_round": 7, "source_key": "components_and_services"},
                },
                {
                    "id": "component-rewards-api",
                    "name": "Rewards API",
                    "trace": {"source_round": 7, "source_key": "components_and_services"},
                },
            ],
            "interfaces_and_integrations": ["Member app calls Rewards API."],
            "interface_objects": [
                {
                    "id": "interface-1",
                    "text": "Member app calls Rewards API.",
                    "trace": {"source_round": 7, "source_key": "interfaces_and_integrations"},
                },
            ],
            "runtime_boundaries": ["Rewards API runs as a separate service."],
            "runtime_boundary_objects": [
                {
                    "id": "runtime-boundary-1",
                    "text": "Rewards API runs as a separate service.",
                    "trace": {"source_round": 7, "source_key": "runtime_boundaries"},
                },
            ],
        }

        rendered = render_requirements_spec(model)

        self.assertIn("## Logical View", rendered)
        self.assertIn("`entity-member` Member [source: round 5 domain_entities]", rendered)
        self.assertIn("## Process View", rendered)
        self.assertIn(
            "`state-transition-1` Requested -> Approved -> Fulfilled [source: round 6 states_and_transitions]",
            rendered,
        )
        self.assertIn("## Architecture View", rendered)
        self.assertIn(
            "`runtime-boundary-1` Rewards API runs as a separate service. [source: round 7 runtime_boundaries]",
            rendered,
        )

    def test_requirements_render_includes_traceability_sections(self) -> None:
        """Requirements rendering should surface cross-view traceability links when present."""
        model = build_model()
        model["traceability"] = {
            "requirement_to_use_case": [
                {
                    "id": "trace-req-uc-1",
                    "from_id": "functional-requirement-1",
                    "to_id": "redeem-reward",
                    "basis": "requirement statement references use-case name",
                }
            ],
            "use_case_to_analysis": [
                {
                    "id": "trace-uc-analysis-1",
                    "from_id": "redeem-reward",
                    "to_id": "entity-reward",
                    "basis": "use-case text references analysis object name",
                }
            ],
            "analysis_to_design": [
                {
                    "id": "trace-analysis-design-1",
                    "from_id": "entity-reward",
                    "to_id": "component-rewards-api",
                    "basis": "design component name references analysis object name",
                }
            ],
        }

        rendered = render_requirements_spec(model)

        self.assertIn("## Requirement To Use-Case Traceability", rendered)
        self.assertIn(
            "`trace-req-uc-1` functional-requirement-1 -> redeem-reward",
            rendered,
        )
        self.assertIn("## Use-Case To Analysis Traceability", rendered)
        self.assertIn("## Analysis To Design Traceability", rendered)

    def test_use_case_render_includes_process_and_architecture_sections(self) -> None:
        """Use-case rendering should include relevant process and architecture sections when present."""
        from specops_tools.render import render_use_case_model

        model = build_model()
        model["process_view"] = {
            "states_and_transitions": ["Requested -> Approved -> Fulfilled"],
            "state_transition_objects": [
                {
                    "id": "state-transition-1",
                    "text": "Requested -> Approved -> Fulfilled",
                    "trace": {"source_round": 6, "source_key": "states_and_transitions"},
                },
            ],
            "triggers_and_approvals": ["Approval is required for manual fulfillment."],
            "trigger_objects": [
                {
                    "id": "trigger-1",
                    "text": "Approval is required for manual fulfillment.",
                    "trace": {"source_round": 6, "source_key": "triggers_and_approvals"},
                },
            ],
        }
        model["architecture_view"] = {
            "interfaces_and_integrations": ["Member app calls Rewards API."],
            "interface_objects": [
                {
                    "id": "interface-1",
                    "text": "Member app calls Rewards API.",
                    "trace": {"source_round": 7, "source_key": "interfaces_and_integrations"},
                },
            ],
        }

        rendered = render_use_case_model(model)

        self.assertIn("## States and Transitions", rendered)
        self.assertIn(
            "`state-transition-1` Requested -> Approved -> Fulfilled [source: round 6 states_and_transitions]",
            rendered,
        )
        self.assertIn("## Interfaces and Integrations", rendered)
        self.assertIn(
            "`interface-1` Member app calls Rewards API. [source: round 7 interfaces_and_integrations]",
            rendered,
        )

    def test_use_case_render_includes_traceability_sections(self) -> None:
        """Use-case rendering should surface use-case traceability links when present."""
        from specops_tools.render import render_use_case_model

        model = build_model()
        model["traceability"] = {
            "requirement_to_use_case": [
                {
                    "id": "trace-req-uc-1",
                    "from_id": "functional-requirement-1",
                    "to_id": "redeem-reward",
                    "basis": "requirement statement references use-case name",
                }
            ],
            "use_case_to_analysis": [
                {
                    "id": "trace-uc-analysis-1",
                    "from_id": "redeem-reward",
                    "to_id": "entity-reward",
                    "basis": "use-case text references analysis object name",
                }
            ],
        }

        rendered = render_use_case_model(model)

        self.assertIn("## Requirement To Use-Case Traceability", rendered)
        self.assertIn("## Use-Case To Analysis Traceability", rendered)
        self.assertIn(
            "`trace-uc-analysis-1` redeem-reward -> entity-reward",
            rendered,
        )

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
