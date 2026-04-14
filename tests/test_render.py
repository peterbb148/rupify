"""Tests for rendering SpecOps artifacts."""

from __future__ import annotations

import unittest

from specops_tools.discovery import normalize_replay_to_model
from specops_tools.interview import replay_session
from specops_tools.render import (
    render_all,
    render_deployment_model,
    render_domain_model,
    render_interaction_model,
    render_requirements_spec,
    render_state_model,
)
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

    def test_render_prefers_layer_collections_when_present(self) -> None:
        """Rendering should remain coherent when analysis/design objects live under layer sections."""
        from specops_tools.render import render_use_case_model

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

    def test_state_model_render_includes_process_traceability(self) -> None:
        """State-model rendering should surface process semantics and relevant trace links."""
        model = build_model()
        model["analysis_view"] = {
            "state_entity_objects": [
                {
                    "id": "state-entity-redemption-request",
                    "name": "Redemption Request",
                    "trace": {"source_round": 6, "source_key": "state_entities"},
                }
            ],
            "state_transition_objects": [
                {
                    "id": "state-transition-1",
                    "text": "Requested -> Approved -> Fulfilled",
                    "trace": {"source_round": 6, "source_key": "states_and_transitions"},
                }
            ],
            "trigger_objects": [
                {
                    "id": "trigger-1",
                    "text": "Approval event moves request to Approved.",
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
        self.assertIn("## State Transitions", rendered)
        self.assertIn("Requested -> Approved -> Fulfilled", rendered)
        self.assertIn("## Use-Case To State Traceability", rendered)
        self.assertIn("`trace-uc-analysis-1` uc-redeem -> state-entity-redemption-request", rendered)
        self.assertIn("## State To Design Traceability", rendered)
        self.assertIn(
            "`trace-analysis-design-1` state-entity-redemption-request -> component-rewards-api",
            rendered,
        )

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

    def test_render_all_includes_state_model_artifact(self) -> None:
        """Primary rendering should emit the formal state-model artifact."""
        outputs = render_all(build_model())

        self.assertIn("deployment-model.md", outputs)
        self.assertIn("domain-model.md", outputs)
        self.assertIn("interaction-model.md", outputs)
        self.assertIn("state-model.md", outputs)
        self.assertTrue(outputs["deployment-model.md"].startswith("# Deployment Model"))
        self.assertTrue(outputs["domain-model.md"].startswith("# Domain Model"))
        self.assertTrue(outputs["interaction-model.md"].startswith("# Interaction Model"))
        self.assertTrue(outputs["state-model.md"].startswith("# State Model"))

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
        self.assertIn("Draft -> Submitted -> Approved", rendered)

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
