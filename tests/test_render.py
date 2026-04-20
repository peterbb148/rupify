"""Tests for rendering Rupify artifacts."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from rupify_tools.discovery import normalize_replay_to_model
from rupify_tools.interview import replay_session
from rupify_tools.render_cli import main as render_cli_main
from rupify_tools.render import (
    render_all,
    render_artifact_family,
    render_deployment_model,
    render_deployment_mermaid,
    render_domain_model,
    render_domain_mermaid,
    render_formal_artifacts,
    render_interaction_mermaid,
    render_interaction_model,
    render_requirements_spec,
    render_scenario_documents,
    render_system_document,
    render_use_case_documents,
    render_state_mermaid,
    render_state_model,
)
from rupify_tools.ucp import calculate_ucp, render_ucp_markdown

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

    def test_render_system_document_includes_risks_use_cases_and_architecture(self) -> None:
        """System document rendering should cover the template-driven system/subsystem sections."""
        model = build_model()
        model["analysis_view"] = {
            "use_cases": [
                {
                    "id": "uc-redeem",
                    "name": "Redeem Reward",
                    "primary_actor": "Customer",
                    "goal": "Redeem a reward.",
                    "priority": "high",
                    "status": "confirmed",
                }
            ],
            "risk_objects": [
                {
                    "id": "risk-data-quality",
                    "name": "Data quality gaps",
                    "description": "Imported member profiles are incomplete.",
                    "priority": "high",
                    "status": "open",
                    "mitigation": "Add onboarding validation",
                    "trace": {"source_round": 12, "source_key": "risks"},
                }
            ],
        }
        model["design_view"] = {
            "component_objects": [
                {
                    "id": "component-member-app",
                    "name": "Member App",
                    "description": "Customer-facing entry point.",
                    "trace": {"source_round": 7, "source_key": "components_and_services"},
                }
            ],
            "interface_objects": [
                {
                    "id": "interface-1",
                    "text": "Member App calls Rewards API.",
                    "trace": {"source_round": 7, "source_key": "interfaces_and_integrations"},
                }
            ],
            "runtime_boundary_objects": [
                {
                    "id": "runtime-boundary-1",
                    "text": "Rewards API runs as a separate service.",
                    "trace": {"source_round": 7, "source_key": "runtime_boundaries"},
                }
            ],
        }
        model["traceability"] = {
            "artifact_lineage": [
                {
                    "id": "trace-artifact-system-document-risk-factors-risk-data-quality",
                    "from_id": "risk-data-quality",
                    "to_artifact": "system-document.md",
                    "artifact_section": "risk factors",
                    "basis": "canonical risk factors object renders into system-document.md",
                }
            ]
        }

        rendered = render_system_document(model)

        self.assertTrue(rendered.startswith("# System / Subsystem Document"))
        self.assertIn("## Risk Factors", rendered)
        self.assertIn("Data quality gaps", rendered)
        self.assertIn("priority: high", rendered)
        self.assertIn("## System-Level Use Cases", rendered)
        self.assertIn("Redeem Reward", rendered)
        self.assertIn("## System-Level Diagram References", rendered)
        self.assertIn("`use-case-model.md`", rendered)
        self.assertIn("## Subsystem Descriptions", rendered)
        self.assertIn("`component-member-app` Member App: Customer-facing entry point.", rendered)
        self.assertIn("system-document.md#risk factors", rendered)

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

    def test_requirements_render_includes_acceptance_constraints_and_ambiguities(self) -> None:
        """Requirements rendering should surface structured acceptance and ambiguity objects."""
        model = build_model()
        model["requirements"] = {
            "functional": [],
            "non_functional": [],
            "acceptance_constraint_objects": [
                {
                    "id": "acceptance-constraint-1",
                    "description": "Security: SSO required",
                    "constraint_kind": "non_functional_requirement",
                    "source_requirement_id": "non_functional-requirement-1",
                    "linked_use_case_ids": ["uc-redeem"],
                    "content_semantics": "normative",
                    "readiness": {"status": "ready"},
                    "trace": {"source_round": 2, "source_key": "constraints"},
                }
            ],
        }
        model["analysis_view"] = {
            "ambiguity_objects": [
                {
                    "id": "ambiguity-open-question-1",
                    "ambiguity_type": "open_question",
                    "description": "Should partner merchants count as actors in V1?",
                    "applies_to_element_ids": ["customer"],
                    "blocking_for_downstream": True,
                    "resolution_status": "open",
                    "content_semantics": "informative",
                    "readiness": {"status": "ready"},
                    "trace": {},
                }
            ]
        }

        rendered = render_requirements_spec(model)

        self.assertIn("## Acceptance Constraints", rendered)
        self.assertIn("Security: SSO required", rendered)
        self.assertIn("semantics: normative", rendered)
        self.assertIn("kind: non_functional_requirement", rendered)
        self.assertIn("use cases: uc-redeem", rendered)
        self.assertIn("## Ambiguities", rendered)
        self.assertIn("type: open_question", rendered)
        self.assertIn("blocking: yes", rendered)

    def test_render_prefers_layer_collections_when_present(self) -> None:
        """Rendering should remain coherent when analysis/design objects live under layer sections."""
        from rupify_tools.render import render_use_case_model

        model = build_model()
        model["actors"] = []
        model["use_cases"] = []
        model["analysis_view"] = {
            "actors": [
                {
                    "id": "member",
                    "name": "Member",
                    "type": "human",
                    "complexity": "average",
                    "description": "",
                    "trace": {"source_round": 3, "source_key": "actors"},
                }
            ],
            "use_cases": [
                {
                    "id": "redeem-reward",
                    "name": "Redeem Reward",
                    "primary_actor": "Member",
                    "goal": "Redeem Reward",
                    "complexity": "average",
                    "main_success_scenario": [],
                    "extensions": [],
                    "trace": {"source_round": 3, "source_key": "use_cases"},
                }
            ],
            "state_transition_objects": [
                {
                    "id": "state-transition-1",
                    "text": "Requested -> Approved",
                    "trace": {"source_round": 6, "source_key": "states_and_transitions"},
                }
            ],
            "trigger_objects": [],
        }
        model["design_view"] = {
            "interface_objects": [
                {
                    "id": "interface-1",
                    "text": "App calls API",
                    "trace": {"source_round": 7, "source_key": "interfaces_and_integrations"},
                }
            ]
        }

        rendered = render_use_case_model(model)

        self.assertIn("`member` Member", rendered)
        self.assertIn("### Redeem Reward", rendered)
        self.assertIn("`state-transition-1` Requested -> Approved", rendered)
        self.assertIn("`interface-1` App calls API", rendered)

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
        from rupify_tools.render import render_use_case_model

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
        from rupify_tools.render import render_use_case_model

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

    def test_render_use_case_documents_includes_template_sections(self) -> None:
        """Compiled use-case documents should render the richer template-driven fields."""
        model = build_model()
        model["analysis_view"] = {
            "actors": [
                {
                    "id": "customer",
                    "name": "Customer",
                    "type": "human",
                    "complexity": "complex",
                    "description": "Redeems rewards in the app.",
                },
                {
                    "id": "ops-manager",
                    "name": "Operations Manager",
                    "type": "human",
                    "complexity": "average",
                    "description": "Approves reward exceptions.",
                },
            ],
            "use_cases": [
                {
                    "id": "uc-redeem",
                    "name": "Redeem Reward",
                    "primary_actor": "Customer",
                    "supporting_actor_ids": ["ops-manager"],
                    "goal": "Redeem a reward.",
                    "trigger": "Customer selects a reward.",
                    "preconditions": ["Member has enough points."],
                    "postconditions": ["Redemption is recorded."],
                    "priority": "high",
                    "status": "confirmed",
                    "complexity": "complex",
                    "main_success_scenario": ["Customer selects reward.", "System validates points."],
                    "extensions": ["Reward is no longer available."],
                    "extension_points": ["Manual approval"],
                    "used_use_case_ids": ["uc-browse"],
                    "subordinate_use_case_ids": ["uc-analytics"],
                    "ui_notes": ["Show point balance before confirmation."],
                    "participating_analysis_object_ids": ["entity-reward"],
                    "other_artifact_refs": ["storyboards/redeem-reward.png"],
                    "other_requirement_ids": ["functional-requirement-1"],
                    "scenario_ids": ["scenario-happy-path"],
                    "trace": {"source_round": 3, "source_key": "use_cases"},
                },
                {
                    "id": "uc-browse",
                    "name": "Browse Rewards",
                    "primary_actor": "Customer",
                    "supporting_actor_ids": [],
                    "goal": "View available rewards.",
                    "trigger": "",
                    "preconditions": [],
                    "postconditions": [],
                    "priority": "",
                    "status": "",
                    "complexity": "average",
                    "main_success_scenario": [],
                    "extensions": [],
                    "extension_points": [],
                    "used_use_case_ids": [],
                    "subordinate_use_case_ids": [],
                    "ui_notes": [],
                    "participating_analysis_object_ids": [],
                    "other_artifact_refs": [],
                    "other_requirement_ids": [],
                    "scenario_ids": [],
                    "trace": {"source_round": 3, "source_key": "use_cases"},
                },
                {
                    "id": "uc-analytics",
                    "name": "Review Redemption Analytics",
                    "primary_actor": "Operations Manager",
                    "supporting_actor_ids": [],
                    "goal": "Inspect redemption metrics.",
                    "trigger": "",
                    "preconditions": [],
                    "postconditions": [],
                    "priority": "",
                    "status": "",
                    "complexity": "simple",
                    "main_success_scenario": [],
                    "extensions": [],
                    "extension_points": [],
                    "used_use_case_ids": [],
                    "subordinate_use_case_ids": [],
                    "ui_notes": [],
                    "participating_analysis_object_ids": [],
                    "other_artifact_refs": [],
                    "other_requirement_ids": [],
                    "scenario_ids": [],
                    "trace": {"source_round": 3, "source_key": "use_cases"},
                },
            ],
            "scenario_objects": [
                {
                    "id": "scenario-happy-path",
                    "name": "Happy path redemption",
                    "use_case_id": "uc-redeem",
                    "use_case_name": "Redeem Reward",
                    "summary": "Primary redemption flow.",
                    "priority": "high",
                    "status": "drafted",
                    "flow_of_events": ["Customer confirms reward.", "System reserves inventory."],
                    "activity_notes": ["Approval step only when inventory is low."],
                    "sequence_notes": ["Customer -> Rewards API -> Ledger"],
                }
            ],
            "requirement_objects": [
                {
                    "id": "functional-requirement-1",
                    "statement": "The system shall record completed redemptions.",
                    "trace": {"source_round": 4, "source_key": "functional_requirements"},
                }
            ],
            "domain_entity_objects": [
                {
                    "id": "entity-reward",
                    "name": "Reward",
                    "description": "Redeemable catalog item.",
                    "trace": {"source_round": 5, "source_key": "domain_entities"},
                }
            ],
            "relationship_objects": [],
            "state_entity_objects": [],
        }
        model["interaction_view"] = {
            "realization_objects": [
                {
                    "id": "interaction-realization-1",
                    "use_case_id": "uc-redeem",
                    "use_case_name": "Redeem Reward",
                    "participant_names": ["Customer", "Rewards API"],
                    "steps": ["Customer selects reward.", "Rewards API validates points."],
                }
            ]
        }
        model["traceability"] = {
            "use_case_to_analysis": [
                {
                    "id": "trace-uc-analysis-1",
                    "from_id": "uc-redeem",
                    "to_id": "entity-reward",
                    "basis": "use-case text references analysis object name",
                }
            ],
            "artifact_lineage": [
                {
                    "id": "trace-artifact-use-case-documents-use-case-documents-uc-redeem",
                    "from_id": "uc-redeem",
                    "to_artifact": "use-case-documents.md",
                    "artifact_section": "use-case documents",
                    "basis": "canonical use-case documents object renders into use-case-documents.md",
                }
            ],
        }

        rendered = render_use_case_documents(model)

        self.assertTrue(rendered.startswith("# Use-Case Documents"))
        self.assertIn("## Redeem Reward", rendered)
        self.assertIn("### Preconditions", rendered)
        self.assertIn("Member has enough points.", rendered)
        self.assertIn("### Used Use Cases", rendered)
        self.assertIn("Browse Rewards", rendered)
        self.assertIn("### Subordinate Use Cases", rendered)
        self.assertIn("Review Redemption Analytics", rendered)
        self.assertIn("### Secondary Scenarios", rendered)
        self.assertIn("#### Happy path redemption", rendered)
        self.assertIn("### User Interface", rendered)
        self.assertIn("Show point balance before confirmation.", rendered)
        self.assertIn("### Linked Requirements", rendered)
        self.assertIn("The system shall record completed redemptions.", rendered)
        self.assertIn("### Sequence and Interaction Notes", rendered)
        self.assertIn("Rewards API validates points.", rendered)
        self.assertIn("use-case-documents.md#use-case documents", rendered)

    def test_render_scenario_documents_includes_template_sections(self) -> None:
        """Compiled scenario documents should render the richer scenario fields."""
        model = build_model()
        model["analysis_view"] = {
            "use_cases": [
                {
                    "id": "uc-redeem",
                    "name": "Redeem Reward",
                }
            ],
            "scenario_objects": [
                {
                    "id": "scenario-happy-path",
                    "name": "Happy path redemption",
                    "use_case_id": "uc-redeem",
                    "use_case_name": "Redeem Reward",
                    "summary": "Primary redemption flow.",
                    "priority": "high",
                    "status": "drafted",
                    "flow_of_events": ["Customer confirms reward.", "System reserves inventory."],
                    "activity_notes": ["Approval step only when inventory is low."],
                    "sequence_notes": ["Customer -> Rewards API -> Ledger"],
                    "other_artifact_refs": ["sequence/redeem-reward.mmd"],
                    "participating_analysis_object_ids": ["entity-reward"],
                    "other_requirement_ids": ["functional-requirement-1"],
                    "trace": {"source_round": 13, "source_key": "scenarios"},
                }
            ],
            "requirement_objects": [
                {
                    "id": "functional-requirement-1",
                    "statement": "The system shall record completed redemptions.",
                    "trace": {"source_round": 4, "source_key": "functional_requirements"},
                }
            ],
            "domain_entity_objects": [
                {
                    "id": "entity-reward",
                    "name": "Reward",
                    "description": "Redeemable catalog item.",
                    "trace": {"source_round": 5, "source_key": "domain_entities"},
                }
            ],
            "relationship_objects": [],
            "state_entity_objects": [],
        }
        model["interaction_view"] = {
            "realization_objects": [
                {
                    "id": "interaction-realization-1",
                    "use_case_id": "uc-redeem",
                    "use_case_name": "Redeem Reward",
                    "participant_names": ["Customer", "Rewards API"],
                    "steps": ["Customer selects reward.", "Rewards API validates points."],
                }
            ]
        }
        model["traceability"] = {
            "use_case_to_analysis": [
                {
                    "id": "trace-uc-analysis-1",
                    "from_id": "uc-redeem",
                    "to_id": "entity-reward",
                    "basis": "use-case text references analysis object name",
                }
            ],
            "artifact_lineage": [
                {
                    "id": "trace-artifact-scenario-documents-scenario-documents-scenario-happy-path",
                    "from_id": "scenario-happy-path",
                    "to_artifact": "scenario-documents.md",
                    "artifact_section": "scenario documents",
                    "basis": "canonical scenario documents object renders into scenario-documents.md",
                }
            ],
        }

        rendered = render_scenario_documents(model)

        self.assertTrue(rendered.startswith("# Scenario Documents"))
        self.assertIn("## Happy path redemption", rendered)
        self.assertIn("Parent Use Case: Redeem Reward", rendered)
        self.assertIn("### Flow of Events", rendered)
        self.assertIn("Customer confirms reward.", rendered)
        self.assertIn("### Activity Notes", rendered)
        self.assertIn("Approval step only when inventory is low.", rendered)
        self.assertIn("### Sequence Notes", rendered)
        self.assertIn("Customer -> Rewards API -> Ledger", rendered)
        self.assertIn("### Interaction Realizations", rendered)
        self.assertIn("Rewards API validates points.", rendered)
        self.assertIn("### Linked Requirements", rendered)
        self.assertIn("The system shall record completed redemptions.", rendered)
        self.assertIn("### Other Artifacts", rendered)
        self.assertIn("sequence/redeem-reward.mmd", rendered)
        self.assertIn("scenario-documents.md#scenario documents", rendered)

    def test_state_model_render_includes_process_traceability(self) -> None:
        """State-model rendering should surface process semantics and relevant trace links."""
        model = build_model()
        model["analysis_view"] = {
            "state_entity_objects": [
                {
                    "id": "state-entity-redemption-request",
                    "name": "Redemption Request",
                    "states": ["Requested", "Approved", "Fulfilled"],
                    "trace": {"source_round": 6, "source_key": "state_entities"},
                }
            ],
            "state_transition_objects": [
                {
                    "id": "state-transition-1",
                    "description": "Requested -> Approved -> Fulfilled",
                    "state_entity_name": "Redemption Request",
                    "from_state": "Requested",
                    "to_state": "Approved",
                    "trigger": "Approval event",
                    "constraint": "manager approval",
                    "is_exception_flow": False,
                    "is_terminal_transition": False,
                    "trace": {"source_round": 6, "source_key": "states_and_transitions"},
                },
                {
                    "id": "state-transition-2",
                    "description": "Approved -> Fulfilled",
                    "state_entity_name": "Redemption Request",
                    "from_state": "Approved",
                    "to_state": "Fulfilled",
                    "trigger": "",
                    "constraint": "",
                    "is_exception_flow": False,
                    "is_terminal_transition": True,
                    "trace": {"source_round": 6, "source_key": "states_and_transitions"},
                }
            ],
            "trigger_objects": [
                {
                    "id": "trigger-1",
                    "description": "Approval event moves request to Approved.",
                    "event_name": "Approval event",
                    "constraint_type": "approval",
                    "approval_required": True,
                    "exceptional_behavior": False,
                    "trace": {"source_round": 6, "source_key": "triggers_and_approvals"},
                }
            ],
        }
        model["design_view"] = {
            "component_objects": [
                {
                    "id": "component-rewards-api",
                    "name": "Rewards API",
                    "trace": {"source_round": 7, "source_key": "components_and_services"},
                }
            ]
        }
        model["traceability"] = {
            "use_case_to_analysis": [
                {
                    "id": "trace-uc-analysis-1",
                    "from_id": "uc-redeem",
                    "to_id": "state-entity-redemption-request",
                    "basis": "use-case text references analysis object name",
                }
            ],
            "analysis_to_design": [
                {
                    "id": "trace-analysis-design-1",
                    "from_id": "state-entity-redemption-request",
                    "to_id": "component-rewards-api",
                    "basis": "design component realizes stateful workflow",
                }
            ],
        }

        rendered = render_state_model(model)

        self.assertIn("# State Model", rendered)
        self.assertIn("## State Entities", rendered)
        self.assertIn("`state-entity-redemption-request` Redemption Request", rendered)
        self.assertIn("{states: Requested, Approved, Fulfilled}", rendered)
        self.assertIn("## State Transitions", rendered)
        self.assertIn("Requested -> Approved", rendered)
        self.assertIn("entity: Redemption Request", rendered)
        self.assertIn("trigger: Approval event", rendered)
        self.assertIn("constraint: manager approval", rendered)
        self.assertIn("terminal transition", rendered)
        self.assertIn("## Triggers and Approvals", rendered)
        self.assertIn("Approval event moves request to Approved.", rendered)
        self.assertIn("type: approval", rendered)
        self.assertIn("approval required", rendered)
        self.assertIn("## Use-Case To State Traceability", rendered)
        self.assertIn("`trace-uc-analysis-1` uc-redeem -> state-entity-redemption-request", rendered)
        self.assertIn("## State To Design Traceability", rendered)
        self.assertIn(
            "`trace-analysis-design-1` state-entity-redemption-request -> component-rewards-api",
            rendered,
        )

    def test_state_model_render_includes_structured_semantic_sections(self) -> None:
        """State-model rendering should surface structured state invariants, guards, and forbidden transitions."""
        model = build_model()
        model["analysis_view"] = {
            "state_entity_objects": [
                {
                    "id": "state-entity-redemption-request",
                    "name": "Redemption Request",
                    "states": ["Requested", "Approved"],
                }
            ],
            "state_transition_objects": [
                {
                    "id": "state-transition-1",
                    "description": "Requested -> Approved",
                    "from_state": "Requested",
                    "to_state": "Approved",
                }
            ],
            "trigger_objects": [],
            "state_invariant_objects": [
                {
                    "id": "state-invariant-1",
                    "description": "Redemption Request must have an owner before approval.",
                    "state_entity_ids": ["state-entity-redemption-request"],
                    "readiness": {"status": "ready"},
                }
            ],
            "guard_condition_objects": [
                {
                    "id": "guard-condition-1",
                    "description": "Approval requires manager approval.",
                    "related_transition_ids": ["state-transition-1"],
                    "source_trigger_id": "trigger-1",
                    "readiness": {"status": "ready"},
                }
            ],
            "forbidden_transition_objects": [
                {
                    "id": "forbidden-transition-1",
                    "description": "Redemption Request cannot move from Approved to Requested.",
                    "related_transition_id": "state-transition-1",
                    "readiness": {"status": "ready"},
                }
            ],
            "ambiguity_objects": [
                {
                    "id": "ambiguity-open-question-1",
                    "ambiguity_type": "open_question",
                    "description": "Should Approved be terminal?",
                    "applies_to_element_ids": ["state-transition-1"],
                    "blocking_for_downstream": True,
                    "resolution_status": "open",
                    "readiness": {"status": "ready"},
                }
            ],
        }
        model["traceability"] = {
            "state_invariant_to_state": [
                {
                    "id": "trace-state-invariant-state-1",
                    "from_id": "state-invariant-1",
                    "to_id": "state-entity-redemption-request",
                }
            ],
            "guard_to_transition": [
                {
                    "id": "trace-guard-transition-1",
                    "from_id": "guard-condition-1",
                    "to_id": "state-transition-1",
                }
            ],
            "forbidden_transition_to_transition": [
                {
                    "id": "trace-forbidden-transition-1",
                    "from_id": "forbidden-transition-1",
                    "to_id": "state-transition-1",
                }
            ],
        }

        rendered = render_state_model(model)

        self.assertIn("## State Invariants", rendered)
        self.assertIn("Redemption Request must have an owner before approval.", rendered)
        self.assertIn("states: state-entity-redemption-request", rendered)
        self.assertIn("## Guard Conditions", rendered)
        self.assertIn("trigger: trigger-1", rendered)
        self.assertIn("transitions: state-transition-1", rendered)
        self.assertIn("## Forbidden Transitions", rendered)
        self.assertIn("transition: state-transition-1", rendered)
        self.assertIn("## State Invariant To State Traceability", rendered)
        self.assertIn("## Guard To Transition Traceability", rendered)
        self.assertIn("## Forbidden Transition Traceability", rendered)
        self.assertIn("## Ambiguities", rendered)
        self.assertIn("readiness:", rendered)

    def test_domain_model_render_includes_logical_traceability(self) -> None:
        """Domain-model rendering should surface logical semantics and relevant trace links."""
        model = build_model()
        model["analysis_view"] = {
            "domain_entity_objects": [
                {
                    "id": "entity-member",
                    "name": "Member",
                    "attributes": ["id", "email"],
                    "trace": {"source_round": 5, "source_key": "domain_entities"},
                }
            ],
            "relationship_objects": [
                {
                    "id": "relationship-1",
                    "description": "A Member redeems Rewards.",
                    "source_multiplicity": "1",
                    "target_multiplicity": "*",
                    "source_role_name": "rewards",
                    "target_role_name": "member",
                    "trace": {"source_round": 5, "source_key": "relationships"},
                }
            ],
            "business_rule_objects": [
                {
                    "id": "business-rule-1",
                    "rule_text": "A Member must have enough points.",
                    "trace": {"source_round": 5, "source_key": "business_rules"},
                }
            ],
        }
        model["traceability"] = {
            "use_case_to_analysis": [
                {
                    "id": "trace-uc-analysis-1",
                    "from_id": "uc-redeem",
                    "to_id": "entity-member",
                    "basis": "use-case text references analysis object name",
                }
            ],
        }

        rendered = render_domain_model(model)

        self.assertIn("# Domain Model", rendered)
        self.assertIn("## Domain Entities", rendered)
        self.assertIn("`entity-member` Member [id, email]", rendered)
        self.assertIn("## Relationships", rendered)
        self.assertIn("A Member redeems Rewards.", rendered)
        self.assertIn("multiplicity: 1 -> *", rendered)
        self.assertIn("roles: rewards / member", rendered)
        self.assertIn("## Business Rules", rendered)
        self.assertIn("A Member must have enough points.", rendered)
        self.assertIn("## Use-Case To Domain Traceability", rendered)
        self.assertIn("`trace-uc-analysis-1` uc-redeem -> entity-member", rendered)
        model["traceability"]["artifact_lineage"] = [
            {
                "id": "trace-artifact-domain-1",
                "from_id": "entity-member",
                "to_artifact": "domain-model.md",
                "artifact_section": "domain entities",
                "basis": "canonical domain entities object renders into domain-model.md",
            }
        ]

        rendered = render_domain_model(model)

        self.assertIn("## Artifact Lineage", rendered)
        self.assertIn("entity-member -> domain-model.md#domain entities", rendered)

    def test_domain_model_render_includes_domain_invariants_and_ambiguities(self) -> None:
        """Domain-model rendering should surface structured domain invariants and ambiguity links."""
        model = build_model()
        model["analysis_view"] = {
            "domain_entity_objects": [
                {
                    "id": "entity-member",
                    "name": "Member",
                }
            ],
            "relationship_objects": [],
            "business_rule_objects": [],
            "domain_invariant_objects": [
                {
                    "id": "domain-invariant-1",
                    "description": "Member must have enough points.",
                    "scope_entity_ids": ["entity-member"],
                    "source_business_rule_id": "business-rule-1",
                }
            ],
            "ambiguity_objects": [
                {
                    "id": "ambiguity-open-question-1",
                    "ambiguity_type": "open_question",
                    "description": "Should guest shoppers count as Members?",
                    "applies_to_element_ids": ["entity-member"],
                    "blocking_for_downstream": True,
                    "resolution_status": "open",
                }
            ],
        }
        model["traceability"] = {
            "domain_invariant_to_entity": [
                {
                    "id": "trace-domain-invariant-entity-1",
                    "from_id": "domain-invariant-1",
                    "to_id": "entity-member",
                }
            ]
        }

        rendered = render_domain_model(model)

        self.assertIn("## Domain Invariants", rendered)
        self.assertIn("scope: entity-member", rendered)
        self.assertIn("business rule: business-rule-1", rendered)
        self.assertIn("## Domain Invariant To Entity Traceability", rendered)
        self.assertIn("## Ambiguities", rendered)
        self.assertIn("blocking: yes", rendered)

    def test_use_case_and_scenario_documents_render_element_semantics(self) -> None:
        """Compiled document families should surface element semantics and readiness."""
        model = build_model()
        model["analysis_view"] = {
            "actors": [],
            "use_cases": [
                {
                    "id": "uc-redeem",
                    "name": "Redeem Reward",
                    "primary_actor": "Customer",
                    "priority": "high",
                    "status": "confirmed",
                    "content_semantics": "normative",
                    "readiness": {"status": "ready"},
                    "complexity": "complex",
                    "goal": "Redeem a reward.",
                    "trigger": "Customer selects reward",
                    "trace": {"source_round": 3, "source_key": "use_cases"},
                    "preconditions": [],
                    "postconditions": [],
                    "extension_points": [],
                    "used_use_case_ids": [],
                    "subordinate_use_case_ids": [],
                    "main_success_scenario": ["Customer selects reward."],
                    "extensions": [],
                    "scenario_ids": ["scenario-happy-path"],
                    "ui_notes": [],
                    "participating_analysis_object_ids": [],
                    "other_requirement_ids": [],
                    "other_artifact_refs": [],
                    "supporting_actor_ids": [],
                }
            ],
            "scenario_objects": [
                {
                    "id": "scenario-happy-path",
                    "name": "Happy Path",
                    "use_case_id": "uc-redeem",
                    "use_case_name": "Redeem Reward",
                    "summary": "Customer redeems a reward",
                    "priority": "high",
                    "status": "confirmed",
                    "content_semantics": "normative",
                    "readiness": {"status": "ready"},
                    "trace": {"source_round": 13, "source_key": "scenarios"},
                    "flow_of_events": ["Customer selects reward."],
                    "activity_notes": [],
                    "sequence_notes": [],
                    "participating_analysis_object_ids": [],
                    "other_requirement_ids": [],
                    "other_artifact_refs": [],
                }
            ],
            "requirement_objects": [],
            "domain_entity_objects": [],
            "relationship_objects": [],
            "state_entity_objects": [],
        }
        model["interaction_view"] = {"realization_objects": []}
        model["traceability"] = {"artifact_lineage": []}

        use_case_rendered = render_use_case_documents(model)
        scenario_rendered = render_scenario_documents(model)

        self.assertIn("- Content Semantics: normative", use_case_rendered)
        self.assertIn("- Readiness: ready", use_case_rendered)
        self.assertIn("- Content Semantics: normative", scenario_rendered)
        self.assertIn("- Readiness: ready", scenario_rendered)

    def test_render_domain_mermaid_outputs_class_diagram(self) -> None:
        """Domain Mermaid rendering should emit a deterministic class diagram."""
        model = build_model()
        model["analysis_view"] = {
            "domain_entity_objects": [
                {
                    "id": "entity-member",
                    "name": "Member",
                    "attributes": ["id", "email"],
                },
                {
                    "id": "entity-reward",
                    "name": "Reward",
                    "attributes": ["id", "pointsCost"],
                },
            ],
            "relationship_objects": [
                {
                    "id": "relationship-1",
                    "relationship_type": "has_many",
                    "source_entity_id": "entity-member",
                    "target_entity_id": "entity-reward",
                    "source_multiplicity": "1",
                    "target_multiplicity": "*",
                }
            ],
        }

        rendered = render_domain_mermaid(model)

        self.assertTrue(rendered.startswith("classDiagram"))
        self.assertIn("class Member {", rendered)
        self.assertIn("+id", rendered)
        self.assertIn("class Reward {", rendered)
        self.assertIn('Member "1" --> "*" Reward : has_many', rendered)

    def test_render_state_mermaid_outputs_state_diagram(self) -> None:
        """State Mermaid rendering should emit a deterministic state diagram."""
        model = build_model()
        model["analysis_view"] = {
            "state_entity_objects": [
                {
                    "id": "state-entity-redemption-request",
                    "name": "Redemption Request",
                    "states": ["Requested", "Approved", "Rejected"],
                }
            ],
            "state_transition_objects": [
                {
                    "id": "state-transition-1",
                    "state_entity_name": "Redemption Request",
                    "from_state": "Requested",
                    "to_state": "Approved",
                    "trigger": "Approval event",
                    "constraint": "manager approval",
                    "is_exception_flow": False,
                    "is_terminal_transition": False,
                },
                {
                    "id": "state-transition-2",
                    "state_entity_name": "Redemption Request",
                    "from_state": "Requested",
                    "to_state": "Rejected",
                    "trigger": "Validation failure",
                    "constraint": "",
                    "is_exception_flow": True,
                    "is_terminal_transition": True,
                },
            ],
        }

        rendered = render_state_mermaid(model)

        self.assertTrue(rendered.startswith("stateDiagram-v2"))
        self.assertIn('state "Redemption Request" as lifecycle {', rendered)
        self.assertIn('state "Requested" as Requested', rendered)
        self.assertIn("Requested --> Approved : Approval event | manager approval", rendered)
        self.assertIn("Requested --> Rejected : Validation failure | exception | terminal", rendered)

    def test_render_interaction_mermaid_outputs_sequence_diagram(self) -> None:
        """Interaction Mermaid rendering should emit a deterministic sequence diagram."""
        model = build_model()
        model["interaction_view"] = {
            "realization_objects": [
                {
                    "id": "interaction-realization-1",
                    "use_case_name": "Redeem Reward",
                    "participant_names": ["Customer", "Rewards API"],
                    "steps": ["Customer selects reward.", "System validates points."],
                }
            ],
            "message_objects": [
                {
                    "id": "interaction-message-1",
                    "source_name": "Member App",
                    "target_name": "Rewards API",
                    "description": "Member App calls Rewards API",
                }
            ],
        }

        rendered = render_interaction_mermaid(model)

        self.assertTrue(rendered.startswith("sequenceDiagram"))
        self.assertIn('participant Customer as "Customer"', rendered)
        self.assertIn('participant Rewards_API as "Rewards API"', rendered)
        self.assertIn("Note over Customer, Rewards_API: Redeem Reward", rendered)
        self.assertIn("Customer->>Rewards_API: Customer selects reward.", rendered)
        self.assertIn("Member_App->>Rewards_API: Member App calls Rewards API", rendered)

    def test_render_deployment_mermaid_outputs_flowchart(self) -> None:
        """Deployment Mermaid rendering should emit a deterministic flowchart."""
        model = build_model()
        model["design_view"] = {
            "component_objects": [
                {"id": "component-member-app", "name": "Member App"},
                {"id": "component-rewards-api", "name": "Rewards API"},
            ],
            "interface_objects": [
                {
                    "id": "interface-1",
                    "source_name": "Member App",
                    "target_name": "Rewards API",
                    "description": "Member App calls Rewards API",
                }
            ],
            "runtime_boundary_objects": [
                {
                    "id": "runtime-boundary-1",
                    "description": "Rewards API runs as a separate service.",
                }
            ],
        }

        rendered = render_deployment_mermaid(model)

        self.assertTrue(rendered.startswith("flowchart LR"))
        self.assertIn('Member_App["Member App"]', rendered)
        self.assertIn('Rewards_API["Rewards API"]', rendered)
        self.assertIn('Member_App -->|"Member App calls Rewards API"| Rewards_API', rendered)
        self.assertIn('RuntimeBoundary_1["Rewards API runs as a separate service."]', rendered)

    def test_render_all_includes_state_model_artifact(self) -> None:
        """Primary rendering should emit the formal state-model artifact."""
        outputs = render_all(build_model())

        self.assertIn("system-document.md", outputs)
        self.assertIn("deployment-model.md", outputs)
        self.assertIn("domain-model.md", outputs)
        self.assertIn("interaction-model.md", outputs)
        self.assertIn("use-case-documents.md", outputs)
        self.assertIn("scenario-documents.md", outputs)
        self.assertIn("state-model.md", outputs)
        self.assertTrue(outputs["system-document.md"].startswith("# System / Subsystem Document"))
        self.assertTrue(outputs["deployment-model.md"].startswith("# Deployment Model"))
        self.assertTrue(outputs["domain-model.md"].startswith("# Domain Model"))
        self.assertTrue(outputs["interaction-model.md"].startswith("# Interaction Model"))
        self.assertTrue(outputs["use-case-documents.md"].startswith("# Use-Case Documents"))
        self.assertTrue(outputs["scenario-documents.md"].startswith("# Scenario Documents"))
        self.assertTrue(outputs["state-model.md"].startswith("# State Model"))

    def test_render_formal_artifacts_skips_ucp_output(self) -> None:
        """Formal rendering should not require or emit the strict UCP artifact."""
        model = build_model()
        model["actors"][0]["complexity"] = "unclassified"

        outputs = render_formal_artifacts(model)

        self.assertIn("system-document.md", outputs)
        self.assertIn("domain-model.md", outputs)
        self.assertIn("interaction-model.md", outputs)
        self.assertIn("deployment-model.md", outputs)
        self.assertIn("use-case-documents.md", outputs)
        self.assertIn("scenario-documents.md", outputs)
        self.assertIn("state-model.md", outputs)
        self.assertNotIn("ucp-estimate.md", outputs)

    def test_render_artifact_family_supports_formal_selection(self) -> None:
        """Artifact-family rendering should allow explicit formal-only selection."""
        model = build_model()
        model["actors"][0]["complexity"] = "unclassified"

        outputs = render_artifact_family(model, "formal")

        self.assertEqual(set(outputs), {
            "system-document.md",
            "requirements-spec.md",
            "use-case-model.md",
            "use-case-documents.md",
            "scenario-documents.md",
            "domain-model.md",
            "interaction-model.md",
            "deployment-model.md",
            "state-model.md",
        })

    def test_render_cli_supports_formal_artifact_family(self) -> None:
        """The renderer CLI should support formal-only output without UCP rendering."""
        model = build_model()
        model["actors"][0]["complexity"] = "unclassified"

        with TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.json"
            output_dir = Path(temp_dir) / "out"
            model_path.write_text(json.dumps(model), encoding="utf-8")

            with patch(
                "sys.argv",
                [
                    "render_cli",
                    "--model",
                    str(model_path),
                    "--output-dir",
                    str(output_dir),
                    "--artifact-family",
                    "formal",
                ],
            ):
                exit_code = render_cli_main()

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "system-document.md").exists())
            self.assertTrue((output_dir / "domain-model.md").exists())
            self.assertTrue((output_dir / "interaction-model.md").exists())
            self.assertTrue((output_dir / "deployment-model.md").exists())
            self.assertTrue((output_dir / "use-case-documents.md").exists())
            self.assertTrue((output_dir / "scenario-documents.md").exists())
            self.assertTrue((output_dir / "state-model.md").exists())
            self.assertFalse((output_dir / "ucp-estimate.md").exists())

    def test_render_cli_supports_domain_mermaid_artifact_family(self) -> None:
        """The renderer CLI should support Mermaid domain diagram output."""
        model = build_model()
        model["analysis_view"] = {
            "domain_entity_objects": [
                {
                    "id": "entity-member",
                    "name": "Member",
                    "attributes": ["id", "email"],
                }
            ],
            "relationship_objects": [],
        }

        with TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.json"
            output_dir = Path(temp_dir) / "out"
            model_path.write_text(json.dumps(model), encoding="utf-8")

            with patch(
                "sys.argv",
                [
                    "render_cli",
                    "--model",
                    str(model_path),
                    "--output-dir",
                    str(output_dir),
                    "--artifact-family",
                    "domain-mermaid",
                ],
            ):
                exit_code = render_cli_main()

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "domain-model.mmd").exists())
            self.assertFalse((output_dir / "ucp-estimate.md").exists())

    def test_render_cli_supports_state_mermaid_artifact_family(self) -> None:
        """The renderer CLI should support Mermaid state diagram output."""
        model = build_model()
        model["analysis_view"] = {
            "state_entity_objects": [
                {
                    "id": "state-entity-redemption-request",
                    "name": "Redemption Request",
                    "states": ["Requested", "Approved"],
                }
            ],
            "state_transition_objects": [
                {
                    "id": "state-transition-1",
                    "from_state": "Requested",
                    "to_state": "Approved",
                    "trigger": "Approval event",
                    "constraint": "",
                    "is_exception_flow": False,
                    "is_terminal_transition": False,
                }
            ],
        }

        with TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.json"
            output_dir = Path(temp_dir) / "out"
            model_path.write_text(json.dumps(model), encoding="utf-8")

            with patch(
                "sys.argv",
                [
                    "render_cli",
                    "--model",
                    str(model_path),
                    "--output-dir",
                    str(output_dir),
                    "--artifact-family",
                    "state-mermaid",
                ],
            ):
                exit_code = render_cli_main()

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "state-model.mmd").exists())
            self.assertFalse((output_dir / "ucp-estimate.md").exists())

    def test_render_cli_supports_interaction_mermaid_artifact_family(self) -> None:
        """The renderer CLI should support Mermaid interaction diagram output."""
        model = build_model()
        model["interaction_view"] = {
            "realization_objects": [
                {
                    "id": "interaction-realization-1",
                    "use_case_name": "Redeem Reward",
                    "participant_names": ["Customer", "Rewards API"],
                    "steps": ["Customer selects reward."],
                }
            ],
            "message_objects": [],
        }

        with TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.json"
            output_dir = Path(temp_dir) / "out"
            model_path.write_text(json.dumps(model), encoding="utf-8")

            with patch(
                "sys.argv",
                [
                    "render_cli",
                    "--model",
                    str(model_path),
                    "--output-dir",
                    str(output_dir),
                    "--artifact-family",
                    "interaction-mermaid",
                ],
            ):
                exit_code = render_cli_main()

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "interaction-model.mmd").exists())
            self.assertFalse((output_dir / "ucp-estimate.md").exists())

    def test_render_cli_supports_deployment_mermaid_artifact_family(self) -> None:
        """The renderer CLI should support Mermaid deployment diagram output."""
        model = build_model()
        model["design_view"] = {
            "component_objects": [
                {"id": "component-member-app", "name": "Member App"}
            ],
            "interface_objects": [],
            "runtime_boundary_objects": [],
        }

        with TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.json"
            output_dir = Path(temp_dir) / "out"
            model_path.write_text(json.dumps(model), encoding="utf-8")

            with patch(
                "sys.argv",
                [
                    "render_cli",
                    "--model",
                    str(model_path),
                    "--output-dir",
                    str(output_dir),
                    "--artifact-family",
                    "deployment-mermaid",
                ],
            ):
                exit_code = render_cli_main()

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "deployment-model.mmd").exists())
            self.assertFalse((output_dir / "ucp-estimate.md").exists())

    def test_render_artifact_family_supports_domain_mermaid_selection(self) -> None:
        """Artifact-family rendering should allow explicit Mermaid domain selection."""
        model = build_model()
        model["analysis_view"] = {
            "domain_entity_objects": [
                {"id": "entity-member", "name": "Member", "attributes": []}
            ],
            "relationship_objects": [],
        }

        outputs = render_artifact_family(model, "domain-mermaid")

        self.assertEqual(set(outputs), {"domain-model.mmd"})
        self.assertTrue(outputs["domain-model.mmd"].startswith("classDiagram"))

    def test_render_artifact_family_supports_state_mermaid_selection(self) -> None:
        """Artifact-family rendering should allow explicit Mermaid state selection."""
        model = build_model()
        model["analysis_view"] = {
            "state_entity_objects": [
                {"id": "state-entity-redemption-request", "name": "Redemption Request", "states": []}
            ],
            "state_transition_objects": [],
        }

        outputs = render_artifact_family(model, "state-mermaid")

        self.assertEqual(set(outputs), {"state-model.mmd"})
        self.assertTrue(outputs["state-model.mmd"].startswith("stateDiagram-v2"))

    def test_render_artifact_family_supports_interaction_mermaid_selection(self) -> None:
        """Artifact-family rendering should allow explicit Mermaid interaction selection."""
        model = build_model()
        model["interaction_view"] = {
            "realization_objects": [],
            "message_objects": [],
        }

        outputs = render_artifact_family(model, "interaction-mermaid")

        self.assertEqual(set(outputs), {"interaction-model.mmd"})
        self.assertTrue(outputs["interaction-model.mmd"].startswith("sequenceDiagram"))

    def test_render_artifact_family_supports_deployment_mermaid_selection(self) -> None:
        """Artifact-family rendering should allow explicit Mermaid deployment selection."""
        model = build_model()
        model["design_view"] = {
            "component_objects": [],
            "interface_objects": [],
            "runtime_boundary_objects": [],
        }

        outputs = render_artifact_family(model, "deployment-mermaid")

        self.assertEqual(set(outputs), {"deployment-model.mmd"})
        self.assertTrue(outputs["deployment-model.mmd"].startswith("flowchart LR"))

    def test_render_all_supports_real_cmdb_fixture(self) -> None:
        """The checked-in CMDB fixture should render the full current bundle, including UCP."""
        repo_root = Path(__file__).resolve().parents[1]
        fixture_path = repo_root / "tests" / "fixtures" / "it_systems_inventory_session.json"
        fixture = json.loads(fixture_path.read_text())

        replay = replay_session(fixture["rounds"])
        model = normalize_replay_to_model(replay)
        outputs = render_all(model)

        self.assertIn("system-document.md", outputs)
        self.assertIn("domain-model.md", outputs)
        self.assertIn("interaction-model.md", outputs)
        self.assertIn("deployment-model.md", outputs)
        self.assertIn("use-case-documents.md", outputs)
        self.assertIn("scenario-documents.md", outputs)
        self.assertIn("state-model.md", outputs)
        self.assertIn("ucp-estimate.md", outputs)
        self.assertTrue(outputs["ucp-estimate.md"].startswith("# UCP Estimate"))

    def test_checked_in_it_systems_inventory_example_bundle_includes_template_documents(self) -> None:
        """The checked-in example bundle should stay aligned with the current formal output family."""
        repo_root = Path(__file__).resolve().parents[1]
        example_dir = repo_root / "examples" / "it-systems-inventory"

        self.assertTrue((example_dir / "system-document.md").exists())
        self.assertTrue((example_dir / "use-case-documents.md").exists())
        self.assertTrue((example_dir / "scenario-documents.md").exists())
        self.assertIn(
            "# System / Subsystem Document",
            (example_dir / "system-document.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "# Use-Case Documents",
            (example_dir / "use-case-documents.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "# Scenario Documents",
            (example_dir / "scenario-documents.md").read_text(encoding="utf-8"),
        )

    def test_interaction_model_render_includes_realizations_and_messages(self) -> None:
        """Interaction-model rendering should surface use-case realizations and message flows."""
        model = build_model()
        model["interaction_view"] = {
            "realization_objects": [
                {
                    "id": "interaction-realization-1",
                    "use_case_id": "uc-redeem",
                    "use_case_name": "Redeem Reward",
                    "participant_ids": ["customer"],
                    "participant_names": ["Customer"],
                    "steps": ["Customer selects reward.", "System validates points."],
                    "trace": {"source_round": 3, "source_key": "use_cases"},
                }
            ],
            "message_objects": [
                {
                    "id": "interaction-message-1",
                    "source_name": "Member App",
                    "source_id": "component-member-app",
                    "target_name": "Rewards API",
                    "target_id": "component-rewards-api",
                    "interaction_verb": "calls",
                    "description": "Member App calls Rewards API",
                    "trace": {"source_round": 7, "source_key": "interfaces_and_integrations"},
                }
            ],
        }

        rendered = render_interaction_model(model)

        self.assertIn("# Interaction Model", rendered)
        self.assertIn("### Redeem Reward", rendered)
        self.assertIn("Customer selects reward.", rendered)
        self.assertIn("## Message Flows", rendered)
        self.assertIn("Member App -> Rewards API", rendered)
        self.assertIn("(calls)", rendered)
        model["traceability"] = {
            "artifact_lineage": [
                {
                    "id": "trace-artifact-interaction-1",
                    "from_id": "interaction-message-1",
                    "to_artifact": "interaction-model.md",
                    "artifact_section": "message flows",
                    "basis": "canonical message flows object renders into interaction-model.md",
                }
            ]
        }

        rendered = render_interaction_model(model)

        self.assertIn("## Artifact Lineage", rendered)
        self.assertIn(
            "interaction-message-1 -> interaction-model.md#message flows",
            rendered,
        )

    def test_end_to_end_interaction_model_pipeline_from_replay(self) -> None:
        """Replay normalization should be able to produce the formal interaction-model artifact."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Rewards system"},
                        {"key": "problem", "answer": "Interaction flow is unclear"},
                        {"key": "in_scope", "answer": "Reward redemption flow"},
                    ],
                },
                {
                    "round": 2,
                    "responses": [
                        {"key": "outcomes", "answer": "Clearer interaction path"},
                    ],
                },
                {
                    "round": 3,
                    "responses": [
                        {"key": "actors", "answer": ["Customer"]},
                        {"key": "use_cases", "answer": ["Redeem Reward"]},
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "components_and_services", "answer": ["Member App", "Rewards API"]},
                        {
                            "key": "interfaces_and_integrations",
                            "answer": ["Member App calls Rewards API"],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        rendered = render_interaction_model(model)

        self.assertIn("Redeem Reward", rendered)
        self.assertIn("Member App -> Rewards API", rendered)

    def test_deployment_model_render_includes_components_and_boundaries(self) -> None:
        """Deployment-model rendering should surface components, interfaces, and boundaries."""
        model = build_model()
        model["design_view"] = {
            "component_objects": [
                {
                    "id": "component-member-app",
                    "name": "Member App",
                    "trace": {"source_round": 7, "source_key": "components_and_services"},
                }
            ],
            "interface_objects": [
                {
                    "id": "interface-1",
                    "description": "Member App calls Rewards API",
                    "trace": {"source_round": 7, "source_key": "interfaces_and_integrations"},
                }
            ],
            "runtime_boundary_objects": [
                {
                    "id": "runtime-boundary-1",
                    "description": "Rewards API runs separately from the UI",
                    "trace": {"source_round": 7, "source_key": "runtime_boundaries"},
                }
            ],
        }

        rendered = render_deployment_model(model)

        self.assertIn("# Deployment Model", rendered)
        self.assertIn("## Components", rendered)
        self.assertIn("`component-member-app` Member App", rendered)
        self.assertIn("## Interfaces and Integrations", rendered)
        self.assertIn("Member App calls Rewards API", rendered)
        self.assertIn("## Runtime Boundaries", rendered)
        self.assertIn("Rewards API runs separately from the UI", rendered)
        model["traceability"] = {
            "artifact_lineage": [
                {
                    "id": "trace-artifact-deployment-1",
                    "from_id": "component-member-app",
                    "to_artifact": "deployment-model.md",
                    "artifact_section": "components",
                    "basis": "canonical components object renders into deployment-model.md",
                }
            ]
        }

        rendered = render_deployment_model(model)

        self.assertIn("## Artifact Lineage", rendered)
        self.assertIn(
            "component-member-app -> deployment-model.md#components",
            rendered,
        )

    def test_end_to_end_deployment_model_pipeline_from_replay(self) -> None:
        """Replay normalization should be able to produce the formal deployment-model artifact."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Rewards system"},
                        {"key": "problem", "answer": "Deployment structure is unclear"},
                        {"key": "in_scope", "answer": "Component and deployment view"},
                    ],
                },
                {
                    "round": 2,
                    "responses": [
                        {"key": "outcomes", "answer": "Clearer deployment understanding"},
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "components_and_services", "answer": ["Member App", "Rewards API"]},
                        {
                            "key": "interfaces_and_integrations",
                            "answer": ["Member App calls Rewards API"],
                        },
                        {
                            "key": "runtime_boundaries",
                            "answer": ["Rewards API runs separately from the UI"],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        rendered = render_deployment_model(model)

        self.assertIn("Member App", rendered)
        self.assertIn("Rewards API", rendered)
        self.assertIn("Rewards API runs separately from the UI", rendered)

    def test_replay_normalization_can_render_system_document_artifact(self) -> None:
        """Replay normalization should be able to produce the formal system-document artifact."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "System inventory"},
                        {"key": "problem", "answer": "System ownership and risk visibility are fragmented."},
                    ],
                },
                {
                    "round": 2,
                    "responses": [
                        {"key": "in_scope", "answer": "Platform system inventory"},
                        {"key": "outcomes", "answer": ["Reduce onboarding risk"]},
                    ],
                },
                {
                    "round": 3,
                    "responses": [
                        {"key": "use_cases", "answer": ["Review system status"]},
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "components_and_services", "answer": ["Inventory API"]},
                        {"key": "interfaces_and_integrations", "answer": ["Dashboard calls Inventory API"]},
                        {"key": "runtime_boundaries", "answer": ["Inventory API runs in a separate service"]},
                    ],
                },
                {
                    "round": 12,
                    "responses": [
                        {
                            "key": "risks",
                            "answer": [
                                "Data quality gaps | priority: high | status: open | mitigation: add ownership validation",
                            ],
                        }
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        rendered = render_system_document(model)

        self.assertIn("System inventory", rendered)
        self.assertIn("Review system status", rendered)
        self.assertIn("Data quality gaps", rendered)
        self.assertIn("Inventory API", rendered)

    def test_replay_normalization_can_render_use_case_documents_artifact(self) -> None:
        """Replay normalization should be able to produce the compiled use-case-documents artifact."""
        replay = replay_session(
            [
                {
                    "round": 3,
                    "responses": [
                        {"key": "actors", "answer": ["Customer"]},
                        {"key": "use_cases", "answer": ["Approve deprecation"]},
                    ],
                },
                {
                    "round": 13,
                    "responses": [
                        {
                            "key": "use_case_details",
                            "answer": ["Approve deprecation | priority: high | status: drafted"],
                        },
                        {
                            "key": "scenarios",
                            "answer": [
                                "Approve deprecation | Happy path approval | Primary approval flow | priority: high | status: drafted",
                            ],
                        },
                        {
                            "key": "ui_notes",
                            "answer": ["Approve deprecation | Show risk summary and approver comments"],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        rendered = render_use_case_documents(model)

        self.assertIn("Approve deprecation", rendered)
        self.assertIn("Priority: high", rendered)
        self.assertIn("Happy path approval", rendered)
        self.assertIn("Show risk summary and approver comments", rendered)

    def test_replay_normalization_can_render_scenario_documents_artifact(self) -> None:
        """Replay normalization should be able to produce the compiled scenario-documents artifact."""
        replay = replay_session(
            [
                {
                    "round": 3,
                    "responses": [
                        {"key": "actors", "answer": ["Customer"]},
                        {"key": "use_cases", "answer": ["Approve deprecation"]},
                    ],
                },
                {
                    "round": 13,
                    "responses": [
                        {
                            "key": "scenarios",
                            "answer": [
                                "Approve deprecation | Happy path approval | Primary approval flow | priority: high | status: drafted | flow: Review request; Approve request",
                            ],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        rendered = render_scenario_documents(model)

        self.assertIn("Happy path approval", rendered)
        self.assertIn("Parent Use Case: Approve deprecation", rendered)
        self.assertIn("Review request", rendered)

    def test_end_to_end_state_model_pipeline_from_replay(self) -> None:
        """Replay normalization should be able to produce the formal state-model artifact."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Workflow system"},
                        {"key": "problem", "answer": "Approval flow is opaque"},
                        {"key": "in_scope", "answer": "Approval lifecycle"},
                    ],
                },
                {
                    "round": 2,
                    "responses": [
                        {"key": "outcomes", "answer": "Clear workflow status"},
                    ],
                },
                {
                    "round": 3,
                    "responses": [
                        {"key": "use_cases", "answer": ["Approve Request"]},
                    ],
                },
                {
                    "round": 4,
                    "responses": [
                        {"key": "workflow_scope", "answer": "Approve Request"},
                    ],
                },
                {
                    "round": 6,
                    "responses": [
                        {"key": "state_entities", "answer": ["Approval Request"]},
                        {
                            "key": "states_and_transitions",
                            "answer": ["Draft -> Submitted -> Approved"],
                        },
                        {
                            "key": "triggers_and_approvals",
                            "answer": ["Submission triggers approval review"],
                        },
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "components_and_services", "answer": ["Approval API"]},
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        rendered = render_state_model(model)

        self.assertIn("Approval Request", rendered)
        self.assertIn("Draft -> Submitted", rendered)
        self.assertIn("Submitted -> Approved", rendered)

    def test_end_to_end_domain_model_pipeline_from_replay(self) -> None:
        """Replay normalization should be able to produce the formal domain-model artifact."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Membership platform"},
                        {"key": "problem", "answer": "Customer and reward rules are unclear"},
                        {"key": "in_scope", "answer": "Reward redemption domain"},
                    ],
                },
                {
                    "round": 2,
                    "responses": [
                        {"key": "outcomes", "answer": "Clear domain language"},
                    ],
                },
                {
                    "round": 3,
                    "responses": [
                        {"key": "use_cases", "answer": ["Redeem Reward"]},
                    ],
                },
                {
                    "round": 5,
                    "responses": [
                        {"key": "domain_entities", "answer": ["Member", "Reward"]},
                        {"key": "relationships", "answer": ["A Member redeems Rewards"]},
                        {
                            "key": "business_rules",
                            "answer": ["A Member must have sufficient points"],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        rendered = render_domain_model(model)

        self.assertIn("Member", rendered)
        self.assertIn("Reward", rendered)
        self.assertIn("A Member redeems Rewards", rendered)

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
