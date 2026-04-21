"""Tests for deterministic interview-to-model normalization."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from rupify_tools.discovery import normalize_replay_to_model
from rupify_tools.interview import replay_session


class DiscoveryTests(unittest.TestCase):
    """Coverage for interview normalization."""

    def test_normalize_replay_to_model_maps_new_view_sections(self) -> None:
        """Replay answers for the new rounds should land in the matching model sections."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Rupify Test"},
                        {"key": "problem", "answer": "Fragmented requirements"},
                        {"key": "in_scope", "answer": "V1.5 interview flow"},
                    ],
                },
                {
                    "round": 2,
                    "responses": [
                        {"key": "outcomes", "answer": ["Clearer specs"]},
                        {"key": "constraints", "answer": ["Web based"]},
                    ],
                },
                {
                    "round": 4,
                    "responses": [
                        {"key": "workflow_scope", "answer": "Support approvals and reviews"},
                        {"key": "metadata_fields", "answer": ["name", "owner"]},
                        {"key": "non_functional_requirements", "answer": ["SSO"]},
                    ],
                },
                {
                    "round": 5,
                    "responses": [
                        {"key": "domain_entities", "answer": ["System", "Approval Request"]},
                        {"key": "relationships", "answer": ["A System has many Approval Requests"]},
                        {"key": "business_rules", "answer": ["Approval requires an owner"]},
                    ],
                },
                {
                    "round": 6,
                    "responses": [
                        {"key": "state_entities", "answer": ["Approval request"]},
                        {
                            "key": "states_and_transitions",
                            "answer": ["Draft -> Submitted -> Approved"],
                        },
                        {
                            "key": "triggers_and_approvals",
                            "answer": ["Submission triggers review"],
                        },
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "components_and_services", "answer": ["Web app", "API"]},
                        {
                            "key": "interfaces_and_integrations",
                            "answer": ["Web app calls API"],
                        },
                        {
                            "key": "runtime_boundaries",
                            "answer": ["API runs separately from the UI"],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)

        self.assertEqual(model["project"]["name"], "Rupify Test")
        self.assertIn("Clearer specs", model["business_goals"])
        self.assertIn("Web based", model["requirements"]["non_functional"])
        self.assertEqual(
            model["requirements"]["functional_objects"][0]["requirement_kind"],
            "functional",
        )
        self.assertEqual(
            model["requirements"]["functional_objects"][0]["model_layer"],
            "analysis",
        )
        self.assertEqual(
            model["requirements"]["non_functional_objects"][0]["requirement_kind"],
            "non_functional",
        )
        self.assertEqual(
            model["analysis_view"]["requirement_ids"][0],
            model["requirements"]["functional_objects"][0]["id"],
        )
        self.assertEqual(
            model["analysis_view"]["requirement_objects"][0]["id"],
            model["requirements"]["functional_objects"][0]["id"],
        )
        self.assertEqual(
            model["analysis_view"]["domain_entity_objects"][0]["id"],
            "entity-system",
        )
        self.assertEqual(
            model["analysis_view"]["domain_entity_objects"][1]["attributes"],
            [],
        )
        self.assertEqual(model["actors"], [])
        self.assertEqual(model["use_cases"], [])
        self.assertIn("System", model["logical_view"]["domain_entities"])
        self.assertEqual(
            model["logical_view"]["domain_entity_objects"][0]["id"],
            "entity-system",
        )
        self.assertEqual(
            model["logical_view"]["domain_entity_objects"][0]["entity_type"],
            "domain_entity",
        )
        self.assertEqual(
            model["logical_view"]["domain_entity_objects"][0]["model_layer"],
            "analysis",
        )
        self.assertEqual(
            model["logical_view"]["domain_entity_objects"][0]["trace"]["source_round"],
            5,
        )
        self.assertEqual(
            model["logical_view"]["relationship_objects"][0]["relationship_type"],
            "has_many",
        )
        self.assertEqual(
            model["logical_view"]["relationship_objects"][0]["source_entity_id"],
            "entity-system",
        )
        self.assertEqual(
            model["logical_view"]["relationship_objects"][0]["source_multiplicity"],
            "1",
        )
        self.assertEqual(
            model["logical_view"]["relationship_objects"][0]["target_multiplicity"],
            "*",
        )
        self.assertIn(
            "Draft -> Submitted -> Approved",
            model["process_view"]["states_and_transitions"],
        )
        self.assertEqual(
            model["process_view"]["state_entity_objects"][0]["id"],
            "state-entity-approval-request",
        )
        self.assertEqual(
            model["process_view"]["state_transition_objects"][0]["from_state"],
            "Draft",
        )
        self.assertEqual(
            model["process_view"]["state_transition_objects"][0]["to_state"],
            "Submitted",
        )
        self.assertEqual(
            model["process_view"]["state_transition_objects"][0]["state_entity_id"],
            "state-entity-approval-request",
        )
        self.assertEqual(
            model["process_view"]["state_entity_objects"][0]["states"],
            ["Draft", "Submitted", "Approved"],
        )
        self.assertEqual(
            model["process_view"]["trigger_objects"][0]["event_name"],
            "Submission",
        )
        self.assertEqual(
            model["process_view"]["trigger_objects"][0]["constraint_type"],
            "event",
        )
        self.assertIn("Web app", model["architecture_view"]["components_and_services"])
        self.assertEqual(
            model["architecture_view"]["component_objects"][0]["id"],
            "component-web-app",
        )
        self.assertEqual(
            model["architecture_view"]["component_objects"][0]["component_kind"],
            "application",
        )
        self.assertEqual(
            model["architecture_view"]["component_objects"][0]["model_layer"],
            "design",
        )
        self.assertEqual(
            model["architecture_view"]["component_objects"][0]["trace"]["source_key"],
            "components_and_services",
        )
        self.assertEqual(
            model["design_view"]["component_ids"][0],
            model["architecture_view"]["component_objects"][0]["id"],
        )
        self.assertEqual(
            model["design_view"]["component_objects"][0]["id"],
            "component-web-app",
        )
        self.assertEqual(
            model["architecture_view"]["interface_objects"][0]["source_component_id"],
            "component-web-app",
        )
        self.assertEqual(
            model["architecture_view"]["interface_objects"][0]["target_component_id"],
            "component-api",
        )
        self.assertEqual(
            model["architecture_view"]["runtime_boundary_objects"][0]["boundary_type"],
            "runtime_separation",
        )
        self.assertEqual(model["interaction_view"]["realization_objects"], [])
        self.assertEqual(
            model["interaction_view"]["message_objects"][0]["interaction_verb"],
            "calls",
        )
        self.assertEqual(
            model["logical_view"]["domain_entity_objects"],
            model["analysis_view"]["domain_entity_objects"],
        )
        self.assertEqual(
            model["process_view"]["state_entity_objects"],
            model["analysis_view"]["state_entity_objects"],
        )
        self.assertEqual(
            model["architecture_view"]["component_objects"],
            model["design_view"]["component_objects"],
        )

    def test_normalize_replay_to_model_reindexes_combined_requirement_batches(self) -> None:
        """Requirement ids should remain unique when multiple rounds contribute the same family."""
        replay = replay_session(
            [
                {
                    "round": 2,
                    "responses": [
                        {"key": "constraints", "answer": ["Web based"]},
                    ],
                },
                {
                    "round": 3,
                    "responses": [
                        {"key": "integrations", "answer": "Export data to reporting systems"},
                    ],
                },
                {
                    "round": 4,
                    "responses": [
                        {"key": "workflow_scope", "answer": "Support approvals"},
                        {"key": "non_functional_requirements", "answer": ["SSO", "Audit trail"]},
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)

        self.assertEqual(
            [item["id"] for item in model["requirements"]["functional_objects"]],
            ["functional-requirement-1", "functional-requirement-2"],
        )
        self.assertEqual(
            [item["id"] for item in model["requirements"]["non_functional_objects"]],
            [
                "non_functional-requirement-1",
                "non_functional-requirement-2",
                "non_functional-requirement-3",
            ],
        )

    def test_normalize_replay_to_model_derives_requirement_sub_obligations(self) -> None:
        """Requirement objects should carry explicit sub-obligations for safe shared-prefix splits."""
        replay = replay_session(
            [
                {
                    "round": 4,
                    "responses": [
                        {
                            "key": "workflow_scope",
                            "answer": (
                                "The system must allow operations managers to maintain reward catalog "
                                "entries and campaign rules."
                            ),
                        },
                        {
                            "key": "non_functional_requirements",
                            "answer": [
                                "The platform must integrate with payment confirmation and downstream reporting sources."
                            ],
                        },
                    ],
                }
            ]
        )

        model = normalize_replay_to_model(replay)

        functional_sub_obligations = model["requirements"]["functional_objects"][0]["sub_obligations"]
        self.assertEqual(
            [item["title"] for item in functional_sub_obligations],
            ["Maintain reward catalog entries", "Maintain campaign rules"],
        )
        self.assertEqual(
            functional_sub_obligations[0]["semantic_id"],
            "functional-requirement-1-obligation-maintain-reward-catalog-entries",
        )
        self.assertEqual(
            functional_sub_obligations[0]["parent_requirement_id"],
            "functional-requirement-1",
        )
        self.assertEqual(functional_sub_obligations[0]["order_index"], 1)
        self.assertEqual(
            functional_sub_obligations[0]["derivation_basis"],
            "allow_shared_verb_objects",
        )
        self.assertIn(
            "Operations managers can maintain reward catalog entries.",
            functional_sub_obligations[0]["acceptance"],
        )

        non_functional_sub_obligations = model["requirements"]["non_functional_objects"][0][
            "sub_obligations"
        ]
        self.assertEqual(
            [item["title"] for item in non_functional_sub_obligations],
            [
                "Integrate with payment confirmation",
                "Integrate with downstream reporting sources",
            ],
        )

    def test_normalize_replay_to_model_derives_requirement_sub_obligations_for_such_as_support(self) -> None:
        """Enumerated `support ... such as` requirements should promote explicit clause structure."""
        replay = replay_session(
            [
                {
                    "round": 2,
                    "responses": [
                        {
                            "key": "constraints",
                            "answer": [
                                (
                                    "The platform must support integrations with external systems "
                                    "such as payment confirmation and reporting sources."
                                )
                            ],
                        },
                    ],
                }
            ]
        )

        model = normalize_replay_to_model(replay)
        sub_obligations = model["requirements"]["non_functional_objects"][0]["sub_obligations"]

        self.assertEqual(
            [item["title"] for item in sub_obligations],
            [
                "Support integration with external systems with payment confirmation",
                "Support integration with external systems with reporting sources",
            ],
        )
        self.assertEqual(
            [item["id"] for item in sub_obligations],
            [
                "support-integration-with-external-systems-with-payment-confirmation",
                "support-integration-with-external-systems-with-reporting-sources",
            ],
        )
        self.assertEqual(
            sub_obligations[0]["semantic_id"],
            (
                "non_functional-requirement-1-obligation-"
                "support-integration-with-external-systems-with-payment-confirmation"
            ),
        )
        self.assertEqual(sub_obligations[1]["order_index"], 2)
        self.assertEqual(
            sub_obligations[0]["derivation_basis"],
            "support_such_as_objects",
        )

    def test_normalize_replay_to_model_keeps_empty_sections_explicit(self) -> None:
        """Missing optional view rounds should still produce stable empty sections."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Rupify Test"},
                        {"key": "problem", "answer": "Fragmented requirements"},
                    ],
                }
            ]
        )

        model = normalize_replay_to_model(replay)

        self.assertEqual(model["logical_view"]["domain_entities"], [])
        self.assertEqual(model["logical_view"]["domain_entity_objects"], [])
        self.assertEqual(model["process_view"]["state_entities"], [])
        self.assertEqual(model["process_view"]["state_entity_objects"], [])
        self.assertEqual(model["architecture_view"]["components_and_services"], [])
        self.assertEqual(model["architecture_view"]["component_objects"], [])
        self.assertEqual(model["analysis_view"]["scenario_objects"], [])
        self.assertEqual(model["analysis_view"]["risk_objects"], [])
        self.assertEqual(model["scenarios"], [])
        self.assertEqual(model["risks"], [])
        self.assertEqual(model["actors"], [])
        self.assertEqual(model["use_cases"], [])

    def test_normalize_replay_to_model_derives_use_case_step_sub_actions(self) -> None:
        """Use-case step objects should expose safe explicit sub-actions with lineage and order."""
        replay = replay_session(
            [
                {
                    "round": 3,
                    "responses": [
                        {
                            "key": "use_cases",
                            "answer": ["Redeem Reward"],
                        },
                    ],
                },
                {
                    "round": 13,
                    "responses": [
                        {
                            "key": "use_case_details",
                            "answer": [
                                (
                                    "Redeem Reward | flow: "
                                    "System validates reward eligibility and available points; "
                                    "System reserves the reward and updates the member balance; "
                                    "System validates and publishes the change; "
                                    "Customer provides the required details and consents"
                                ),
                            ],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        step_objects = model["analysis_view"]["use_case_step_objects"]

        self.assertEqual(
            [item["title"] for item in step_objects[0]["sub_actions"]],
            ["Validate reward eligibility", "Validate available points"],
        )
        self.assertEqual(
            step_objects[0]["sub_actions"][0]["derivation_basis"],
            "shared_verb_objects",
        )
        self.assertEqual(
            step_objects[0]["sub_actions"][0]["parent_step_id"],
            "redeem-reward-step-1",
        )
        self.assertEqual(step_objects[0]["sub_actions"][0]["order_index"], 1)
        self.assertEqual(
            [item["title"] for item in step_objects[1]["sub_actions"]],
            ["Reserve the reward", "Update the member balance"],
        )
        self.assertEqual(
            [item["title"] for item in step_objects[2]["sub_actions"]],
            ["Validate the change", "Publish the change"],
        )
        self.assertEqual(step_objects[3]["sub_actions"], [])

    def test_normalize_replay_to_model_maps_actors_and_use_cases(self) -> None:
        """Round-3 actor and use-case discovery should produce structured canonical objects."""
        replay = replay_session(
            [
                {
                    "round": 3,
                    "responses": [
                        {
                            "key": "actors",
                            "answer": ["Operations Manager", "Payment Gateway", "Reporting API"],
                        },
                        {
                            "key": "use_cases",
                            "answer": ["Browse Rewards", "Redeem Reward"],
                        },
                    ],
                }
            ]
        )

        model = normalize_replay_to_model(replay)

        self.assertEqual(model["actors"][0]["id"], "operations-manager")
        self.assertEqual(model["actors"][0]["semantic_id"], "operations-manager")
        self.assertEqual(model["actors"][0]["change_metadata"]["semantic_version"], 1)
        self.assertEqual(model["actors"][0]["change_metadata"]["change_source"], "round_3")
        self.assertTrue(model["actors"][0]["change_metadata"]["semantic_hash"])
        self.assertEqual(model["actors"][0]["type"], "human")
        self.assertEqual(model["actors"][0]["model_layer"], "analysis")
        self.assertEqual(model["actors"][0]["interaction_style"], "user_interface")
        self.assertEqual(model["actors"][0]["responsibilities"], [])
        self.assertEqual(model["actors"][0]["trace"]["source_round"], 3)
        self.assertEqual(model["actors"][1]["type"], "system")
        self.assertEqual(model["actors"][1]["interaction_style"], "system_interface")
        self.assertEqual(model["actors"][2]["type"], "system")
        self.assertEqual(model["use_cases"][0]["id"], "browse-rewards")
        self.assertEqual(model["use_cases"][0]["semantic_id"], "browse-rewards")
        self.assertEqual(model["use_cases"][0]["goal"], "Browse Rewards")
        self.assertEqual(model["use_cases"][0]["model_layer"], "analysis")
        self.assertEqual(model["use_cases"][0]["primary_actor_id"], "")
        self.assertEqual(model["use_cases"][0]["supporting_actor_ids"], [])
        self.assertEqual(model["use_cases"][0]["trigger"], "")
        self.assertEqual(model["use_cases"][0]["preconditions"], [])
        self.assertEqual(model["use_cases"][0]["postconditions"], [])
        self.assertEqual(model["use_cases"][0]["priority"], "")
        self.assertEqual(model["use_cases"][0]["status"], "")
        self.assertEqual(model["use_cases"][0]["extension_points"], [])
        self.assertEqual(model["use_cases"][0]["used_use_case_ids"], [])
        self.assertEqual(model["use_cases"][0]["subordinate_use_case_ids"], [])
        self.assertEqual(model["use_cases"][0]["ui_notes"], [])
        self.assertEqual(model["use_cases"][0]["participating_analysis_object_ids"], [])
        self.assertEqual(model["use_cases"][0]["other_artifact_refs"], [])
        self.assertEqual(model["use_cases"][0]["other_requirement_ids"], [])
        self.assertEqual(model["use_cases"][0]["scenario_ids"], [])
        self.assertEqual(model["use_cases"][0]["trace"]["source_key"], "use_cases")
        self.assertEqual(model["use_cases"][1]["complexity"], "unclassified")
        self.assertEqual(model["analysis_view"]["actor_ids"][0], "operations-manager")
        self.assertEqual(model["analysis_view"]["use_case_ids"][0], "browse-rewards")
        self.assertEqual(model["analysis_view"]["scenario_ids"], [])
        self.assertEqual(model["analysis_view"]["risk_ids"], [])
        self.assertEqual(model["analysis_view"]["scenario_objects"], [])
        self.assertEqual(model["analysis_view"]["risk_objects"], [])
        self.assertEqual(model["scenarios"], [])
        self.assertEqual(model["risks"], [])
        self.assertEqual(model["analysis_view"]["actors"][0]["id"], "operations-manager")
        self.assertEqual(model["analysis_view"]["use_cases"][0]["id"], "browse-rewards")
        self.assertEqual(model["actors"], model["analysis_view"]["actors"])
        self.assertEqual(model["use_cases"], model["analysis_view"]["use_cases"])
        self.assertEqual(
            model["interaction_view"]["realization_objects"][0]["use_case_id"],
            "browse-rewards",
        )
        self.assertEqual(
            model["interaction_view"]["realization_objects"][0]["steps"],
            [],
        )
        self.assertEqual(
            model["interaction_view"]["realization_objects"][0]["semantic_id"],
            "interaction-realization-1",
        )

    def test_normalize_replay_to_model_applies_ucp_answers_to_objects(self) -> None:
        """UCP round answers should update normalized actor/use-case complexity and factors."""
        replay = replay_session(
            [
                {
                    "round": 3,
                    "responses": [
                        {
                            "key": "actors",
                            "answer": ["Operations Manager", "Payment Gateway"],
                        },
                        {
                            "key": "use_cases",
                            "answer": ["Browse Rewards", "Redeem Reward"],
                        },
                    ],
                },
                {
                    "round": 8,
                    "responses": [
                        {
                            "key": "actor_complexity",
                            "answer": [
                                "Operations Manager: average",
                                "Payment Gateway: simple",
                            ],
                        }
                    ],
                },
                {
                    "round": 9,
                    "responses": [
                        {
                            "key": "use_case_complexity",
                            "answer": [
                                "Browse Rewards: average",
                                "Redeem Reward: complex",
                            ],
                        }
                    ],
                },
                {
                    "round": 10,
                    "responses": [
                        {
                            "key": "technical",
                            "answer": "security: 5\nthird-party access: 4\nresponse time: 3",
                        }
                    ],
                },
                {
                    "round": 11,
                    "responses": [
                        {
                            "key": "environmental",
                            "answer": "team familiarity: 4\nmotivation: 5\npart-time staffing: 1",
                        }
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)

        self.assertEqual(model["actors"][0]["complexity"], "average")
        self.assertEqual(model["actors"][0]["complexity_trace"]["source_round"], 8)
        self.assertEqual(model["actors"][1]["complexity"], "simple")
        self.assertEqual(model["use_cases"][0]["complexity"], "average")
        self.assertEqual(model["use_cases"][0]["complexity_trace"]["source_key"], "use_case_complexity")
        self.assertEqual(model["use_cases"][1]["complexity"], "complex")
        self.assertEqual(model["ucp"]["technical_factors"]["special_security"], 5)
        self.assertEqual(model["ucp"]["technical_factors"]["third_party_access"], 4)
        self.assertEqual(model["ucp"]["environmental_factors"]["familiar_with_process"], 4)
        self.assertEqual(model["ucp"]["environmental_factors"]["part_time_staff"], 1)

    def test_normalize_replay_to_model_maps_risks_and_document_detail_fields(self) -> None:
        """Template-driven rounds should populate risks, use-case metadata, scenarios, and UI notes."""
        replay = replay_session(
            [
                {
                    "round": 3,
                    "responses": [
                        {"key": "use_cases", "answer": ["Approve deprecation", "Validate owner"]},
                    ],
                },
                {
                    "round": 12,
                    "responses": [
                        {
                            "key": "risks",
                            "answer": [
                                "Data quality gaps | priority: high | status: open | mitigation: add onboarding validation",
                            ],
                        }
                    ],
                },
                {
                    "round": 13,
                    "responses": [
                        {
                            "key": "use_case_details",
                            "answer": [
                                "Approve deprecation | priority: high | status: drafted | flow: Capture approval request; Validate owner; Submit approval | used: Validate owner",
                            ],
                        },
                        {
                            "key": "scenarios",
                            "answer": [
                                "Approve deprecation | Happy path approval | Primary approval flow | priority: high | status: drafted",
                            ],
                        },
                        {
                            "key": "ui_notes",
                            "answer": [
                                "Approve deprecation | Show risk summary and approver comments",
                            ],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)

        self.assertEqual(model["risks"][0]["name"], "Data quality gaps")
        self.assertEqual(model["risks"][0]["priority"], "high")
        self.assertEqual(model["risks"][0]["status"], "open")
        self.assertEqual(model["risks"][0]["mitigation"], "add onboarding validation")
        self.assertEqual(model["analysis_view"]["risk_ids"], ["risk-data-quality-gaps"])

        self.assertEqual(model["use_cases"][0]["priority"], "high")
        self.assertEqual(model["use_cases"][0]["status"], "drafted")
        self.assertEqual(model["use_cases"][0]["used_use_case_ids"], ["validate-owner"])
        self.assertEqual(
            model["use_cases"][0]["main_success_scenario"],
            ["Capture approval request", "Validate owner", "Submit approval"],
        )
        self.assertEqual(
            model["analysis_view"]["use_case_step_ids"],
            [
                "approve-deprecation-step-1",
                "approve-deprecation-step-2",
                "approve-deprecation-step-3",
            ],
        )
        self.assertEqual(
            model["use_cases"][0]["ui_notes"],
            ["Show risk summary and approver comments"],
        )
        self.assertEqual(model["use_cases"][0]["scenario_ids"], ["scenario-happy-path-approval"])

        self.assertEqual(model["scenarios"][0]["name"], "Happy path approval")
        self.assertEqual(model["scenarios"][0]["use_case_id"], "approve-deprecation")
        self.assertEqual(model["scenarios"][0]["priority"], "high")
        self.assertEqual(model["scenarios"][0]["status"], "drafted")
        self.assertEqual(model["analysis_view"]["scenario_ids"], ["scenario-happy-path-approval"])

    def test_normalize_replay_to_model_adds_model_metadata(self) -> None:
        """Normalization should expose top-level model metadata for downstream diffing."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Inventory system"},
                        {"key": "problem", "answer": "Poor visibility"},
                    ],
                }
            ]
        )

        model = normalize_replay_to_model(replay)

        self.assertEqual(model["model_metadata"]["schema_version"], 1)
        self.assertEqual(model["model_metadata"]["semantic_id"], "rupify-model")
        self.assertEqual(
            model["model_metadata"]["change_metadata"]["change_source"],
            "normalize_replay_to_model",
        )
        self.assertTrue(model["model_metadata"]["change_metadata"]["semantic_hash"])

    def test_normalize_replay_to_model_keeps_semantic_fields_explicit_when_unparsed(self) -> None:
        """Hardening should expose semantic fields even when deterministic parsing finds no structure."""
        replay = replay_session(
            [
                {
                    "round": 5,
                    "responses": [
                        {"key": "domain_entities", "answer": ["Ledger Entry"]},
                        {"key": "relationships", "answer": ["Ledger Entry interacts with reporting"]},
                        {"key": "business_rules", "answer": ["Ledger Entry must be retained"]},
                    ],
                },
                {
                    "round": 6,
                    "responses": [
                        {"key": "states_and_transitions", "answer": ["Manual review path"]},
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "interfaces_and_integrations", "answer": ["Event bridge integration"]},
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)

        relationship = model["logical_view"]["relationship_objects"][0]
        self.assertEqual(relationship["relationship_type"], "")
        self.assertEqual(relationship["source_entity_id"], "")
        self.assertEqual(relationship["target_entity_id"], "")
        self.assertEqual(relationship["source_multiplicity"], "")
        self.assertEqual(relationship["target_multiplicity"], "")
        self.assertEqual(relationship["description"], "Ledger Entry interacts with reporting")

        transition = model["process_view"]["state_transition_objects"][0]
        self.assertEqual(transition["from_state"], "")
        self.assertEqual(transition["to_state"], "")
        self.assertEqual(transition["description"], "Manual review path")

        interface = model["architecture_view"]["interface_objects"][0]
        self.assertEqual(interface["source_component_id"], "")
        self.assertEqual(interface["target_component_id"], "")
        self.assertEqual(interface["interaction_verb"], "")

    def test_normalize_replay_to_model_parses_domain_attributes(self) -> None:
        """Domain entities should parse simple attribute lists when explicitly stated."""
        replay = replay_session(
            [
                {
                    "round": 5,
                    "responses": [
                        {
                            "key": "domain_entities",
                            "answer": ["Member: id, email, points balance"],
                        },
                    ],
                }
            ]
        )

        model = normalize_replay_to_model(replay)

        entity = model["logical_view"]["domain_entity_objects"][0]
        self.assertEqual(entity["name"], "Member")
        self.assertEqual(entity["attributes"], ["id", "email", "points balance"])

    def test_normalize_replay_to_model_adds_requirement_objects(self) -> None:
        """Requirement lists should also have explicit semantic object forms."""
        replay = replay_session(
            [
                {
                    "round": 2,
                    "responses": [
                        {"key": "constraints", "answer": ["Security: SSO required"]},
                    ],
                },
                {
                    "round": 4,
                    "responses": [
                        {"key": "workflow_scope", "answer": "Support change approval flow"},
                        {"key": "non_functional_requirements", "answer": ["Performance: sub-second search"]},
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)

        functional_object = model["requirements"]["functional_objects"][0]
        self.assertEqual(functional_object["statement"], "Support change approval flow")
        self.assertEqual(functional_object["model_layer"], "analysis")
        self.assertEqual(functional_object["linked_use_case_ids"], [])
        self.assertEqual(functional_object["fit_criterion"], "")
        self.assertEqual(
            model["requirements"]["functional"],
            [item["statement"] for item in model["analysis_view"]["requirement_objects"][:1]],
        )

        non_functional_object = model["requirements"]["non_functional_objects"][0]
        self.assertEqual(non_functional_object["statement"], "Security: SSO required")
        self.assertEqual(non_functional_object["quality_attribute"], "Security")
        self.assertEqual(non_functional_object["requirement_kind"], "non_functional")
        self.assertEqual(non_functional_object["model_layer"], "analysis")
        self.assertEqual(
            model["requirements"]["non_functional"],
            [
                item["statement"]
                for item in model["analysis_view"]["requirement_objects"]
                if item["requirement_kind"] == "non_functional"
            ],
        )

    def test_normalize_replay_to_model_builds_cross_view_trace_links(self) -> None:
        """Normalization should create deterministic cross-view links when names match explicitly."""
        replay = replay_session(
            [
                {
                    "round": 3,
                    "responses": [
                        {"key": "actors", "answer": ["Operator"]},
                        {"key": "use_cases", "answer": ["Approve System"]},
                        {"key": "integrations", "answer": "Validate submitted system"},
                    ],
                },
                {
                    "round": 4,
                    "responses": [
                        {"key": "workflow_scope", "answer": "Approve System"},
                    ],
                },
                {
                    "round": 5,
                    "responses": [
                        {"key": "domain_entities", "answer": ["System"]},
                        {"key": "relationships", "answer": ["System has many approvals"]},
                        {"key": "business_rules", "answer": ["Validate submitted system"]},
                    ],
                },
                {
                    "round": 6,
                    "responses": [
                        {"key": "state_entities", "answer": ["System lifecycle"]},
                        {"key": "states_and_transitions", "answer": ["Validate submitted system"]},
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "components_and_services", "answer": ["System API"]},
                        {"key": "interfaces_and_integrations", "answer": ["Validate submitted system"]},
                    ],
                },
                {
                    "round": 13,
                    "responses": [
                        {
                            "key": "use_case_details",
                            "answer": [
                                "Approve System | flow: Validate submitted system; Record approval",
                            ],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)

        self.assertEqual(
            model["traceability"]["requirement_to_use_case"][0]["link_type"],
            "requirement_to_use_case",
        )
        self.assertEqual(
            model["requirements"]["functional_objects"][0]["linked_use_case_ids"],
            ["approve-system"],
        )
        self.assertEqual(
            model["use_cases"][0]["other_requirement_ids"],
            ["functional-requirement-1"],
        )
        self.assertEqual(
            model["traceability"]["use_case_to_analysis"][0]["to_id"],
            "entity-system",
        )
        self.assertEqual(
            model["use_cases"][0]["participating_analysis_object_ids"],
            ["entity-system"],
        )
        self.assertEqual(
            model["traceability"]["analysis_to_design"][0]["to_id"],
            "component-system-api",
        )
        self.assertEqual(
            model["analysis_view"]["use_case_step_ids"],
            ["approve-system-step-1", "approve-system-step-2"],
        )
        self.assertEqual(
            model["analysis_view"]["use_case_step_objects"][0]["text"],
            "Validate submitted system",
        )
        self.assertEqual(
            model["interaction_view"]["realization_objects"][0]["step_objects"][0]["id"],
            "approve-system-realization-step-1",
        )
        self.assertEqual(
            model["traceability"]["requirement_to_step"][0]["to_id"],
            "approve-system-step-1",
        )
        self.assertEqual(
            model["traceability"]["step_to_interaction"][0]["from_id"],
            "approve-system-step-1",
        )
        self.assertEqual(
            model["traceability"]["step_to_transition"][0]["to_id"],
            "state-transition-1",
        )
        self.assertEqual(
            model["traceability"]["business_rule_to_transition"][0]["from_id"],
            "business-rule-1",
        )
        self.assertEqual(
            model["traceability"]["step_to_interaction"][0]["change_metadata"]["change_source"],
            "derived_traceability",
        )
        self.assertEqual(
            model["traceability"]["requirement_to_use_case"][0]["semantic_id"],
            model["traceability"]["requirement_to_use_case"][0]["id"],
        )
        self.assertEqual(
            model["traceability"]["requirement_to_use_case"][0]["change_metadata"]["change_source"],
            "derived_traceability",
        )
        self.assertTrue(
            model["traceability"]["artifact_lineage"][0]["change_metadata"]["semantic_hash"]
        )
        self.assertIn(
            "domain-model.md",
            {
                link["to_artifact"]
                for link in model["traceability"]["artifact_lineage"]
            },
        )
        self.assertIn(
            "interaction-model.md",
            {
                link["to_artifact"]
                for link in model["traceability"]["artifact_lineage"]
            },
        )
        self.assertIn(
            "deployment-model.md",
            {
                link["to_artifact"]
                for link in model["traceability"]["artifact_lineage"]
            },
        )

    def test_normalize_replay_to_model_promotes_structured_invariants_constraints_and_ambiguities(
        self,
    ) -> None:
        """Normalization should expose structured semantic objects for downstream planning."""
        replay = replay_session(
            [
                {
                    "round": 2,
                    "responses": [
                        {"key": "constraints", "answer": ["Security: SSO required"]},
                        {"key": "success_criteria", "answer": ["Approval completes within one day"]},
                    ],
                },
                {
                    "round": 5,
                    "responses": [
                        {"key": "domain_entities", "answer": ["System"]},
                        {
                            "key": "business_rules",
                            "answer": [
                                "System must retain an owner",
                                "System lifecycle cannot move from Approved to Draft",
                            ],
                        },
                    ],
                },
                {
                    "round": 6,
                    "responses": [
                        {"key": "state_entities", "answer": ["System lifecycle"]},
                        {
                            "key": "states_and_transitions",
                            "answer": ["System lifecycle: Draft -> Approved"],
                        },
                        {
                            "key": "triggers_and_approvals",
                            "answer": ["Approval requires manager approval"],
                        },
                    ],
                },
            ]
        )
        replay["assumptions"] = [
            {
                "text": "System ownership rules may change after pilot.",
                "status": "assumed",
                "source": "workshop",
            }
        ]
        replay["open_questions"] = [
            {
                "text": "Should System lifecycle include Archived state?",
                "status": "open",
                "source": "review",
            }
        ]

        model = normalize_replay_to_model(replay)

        self.assertEqual(
            model["requirements"]["acceptance_constraint_objects"][0]["source_requirement_id"],
            "non_functional-requirement-1",
        )
        self.assertEqual(
            model["requirements"]["acceptance_constraint_objects"][1]["constraint_kind"],
            "success_criterion",
        )
        self.assertEqual(
            model["logical_view"]["domain_invariant_objects"][0]["scope_entity_ids"],
            ["entity-system"],
        )
        self.assertEqual(
            model["process_view"]["state_invariant_objects"][0]["state_entity_ids"],
            ["state-entity-system-lifecycle"],
        )
        self.assertEqual(
            model["process_view"]["guard_condition_objects"][0]["related_transition_ids"],
            ["state-transition-1"],
        )
        self.assertEqual(
            model["process_view"]["forbidden_transition_objects"][0]["related_transition_id"],
            "state-transition-1",
        )
        self.assertEqual(model["ambiguities"][0]["ambiguity_type"], "assumption")
        self.assertEqual(model["ambiguities"][1]["resolution_status"], "open")
        self.assertEqual(
            model["traceability"]["domain_invariant_to_entity"][0]["to_id"],
            "entity-system",
        )
        self.assertEqual(
            model["traceability"]["guard_to_transition"][0]["to_id"],
            "state-transition-1",
        )
        self.assertEqual(
            model["traceability"]["acceptance_constraint_to_requirement"][0]["to_id"],
            "non_functional-requirement-1",
        )
        self.assertEqual(
            model["traceability"]["ambiguity_to_element"][0]["to_id"],
            "entity-system",
        )
        self.assertEqual(
            model["logical_view"]["domain_invariant_objects"][0]["content_semantics"],
            "normative",
        )
        self.assertEqual(
            model["requirements"]["acceptance_constraint_objects"][0]["content_semantics"],
            "normative",
        )
        self.assertEqual(model["ambiguities"][0]["content_semantics"], "informative")
        self.assertEqual(
            model["logical_view"]["domain_invariant_objects"][0]["readiness"]["status"],
            "ready",
        )
        self.assertIn(
            "domain-invariant-1",
            model["element_readiness"]["summary"]["ready_normative_ids"],
        )

    def test_normalize_replay_to_model_with_real_fixture(self) -> None:
        """The checked-in interview fixture should normalize into the canonical V1.5 shape."""
        repo_root = Path(__file__).resolve().parents[1]
        fixture_path = repo_root / "tests" / "fixtures" / "it_systems_inventory_session.json"
        fixture = json.loads(fixture_path.read_text())

        replay = replay_session(fixture["rounds"])
        model = normalize_replay_to_model(replay)

        self.assertEqual(
            model["project"]["name"],
            "A system to manage inventory of IT Systems themselves.",
        )
        self.assertIn("UI must be web based", model["requirements"]["non_functional"])
        self.assertIn("System name", model["metadata_fields"])
        self.assertEqual(model["actors"][0]["name"], "Business owners")
        self.assertEqual(model["actors"][0]["type"], "human")
        self.assertEqual(model["use_cases"][0]["name"], "Register a system")
        self.assertIn("System", model["logical_view"]["domain_entities"])
        self.assertGreater(len(model["logical_view"]["relationship_objects"]), 0)
        self.assertIn("System", model["process_view"]["state_entities"])

    def test_normalize_replay_to_model_enriches_state_machine_semantics(self) -> None:
        """State normalization should derive lifecycle semantics when the source text is explicit."""
        replay = replay_session(
            [
                {
                    "round": 6,
                    "responses": [
                        {"key": "state_entities", "answer": ["Approval Request"]},
                        {
                            "key": "states_and_transitions",
                            "answer": [
                                "Approval Request: Draft -> Submitted -> Approved",
                                "Approval Request: Submitted -> Rejected",
                            ],
                        },
                        {
                            "key": "triggers_and_approvals",
                            "answer": [
                                "Submission requires manager approval",
                                "Rejection event moves request to Rejected",
                            ],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        transitions = model["process_view"]["state_transition_objects"]
        triggers = model["process_view"]["trigger_objects"]

        self.assertEqual(transitions[0]["state_entity_name"], "Approval Request")
        self.assertEqual(transitions[1]["is_terminal_transition"], True)
        self.assertEqual(transitions[2]["is_exception_flow"], True)
        self.assertEqual(transitions[2]["is_terminal_transition"], True)
        self.assertEqual(triggers[0]["approval_required"], True)
        self.assertEqual(triggers[0]["constraint_type"], "approval")
        self.assertEqual(triggers[1]["exceptional_behavior"], True)
        self.assertEqual(model["architecture_view"]["runtime_boundary_objects"], [])

    def test_normalize_replay_to_model_derives_guard_parts(self) -> None:
        """Guard-condition objects should expose explicit ordered guard parts for safe patterns."""
        replay = replay_session(
            [
                {
                    "round": 6,
                    "responses": [
                        {"key": "state_entities", "answer": ["Reward Catalog Entry"]},
                        {
                            "key": "states_and_transitions",
                            "answer": [
                                "Reward Catalog Entry: Draft -> Published -> Retired",
                            ],
                        },
                        {
                            "key": "triggers_and_approvals",
                            "answer": [
                                "Payment confirmation triggers redemption fulfillment",
                                "Catalog validation approval is required before a reward becomes Published",
                                "Deprecation approval requires enterprise architect review",
                            ],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        guard_objects = model["process_view"]["guard_condition_objects"]

        self.assertEqual(
            [item["part_kind"] for item in guard_objects[0]["guard_parts"]],
            ["context", "allow_outcome"],
        )
        self.assertEqual(guard_objects[0]["guard_parts"][0]["text"], "Payment confirmation")
        self.assertEqual(
            [item["part_kind"] for item in guard_objects[1]["guard_parts"]],
            ["condition", "allow_outcome", "block_outcome"],
        )
        self.assertEqual(
            guard_objects[1]["guard_parts"][0]["parent_guard_id"],
            "guard-condition-2",
        )
        self.assertEqual(guard_objects[1]["guard_parts"][0]["order_index"], 1)
        self.assertEqual(
            [item["part_kind"] for item in guard_objects[2]["guard_parts"]],
            ["context", "condition", "block_outcome"],
        )

    def test_normalize_replay_to_model_derives_invariant_clauses(self) -> None:
        """Invariant objects should expose explicit clauses for safe conjunctive patterns."""
        replay = replay_session(
            [
                {
                    "round": 5,
                    "responses": [
                        {"key": "domain_entities", "answer": ["System", "Member", "Redemption"]},
                        {
                            "key": "business_rules",
                            "answer": [
                                "A System must record vendor and contract dates.",
                                "A Member must provide the required details and consents before enrollment completes.",
                                "A Redemption must not be fulfilled unless reward eligibility and available points are confirmed.",
                            ],
                        },
                    ],
                },
                {
                    "round": 6,
                    "responses": [
                        {"key": "state_entities", "answer": ["Redemption"]},
                        {
                            "key": "states_and_transitions",
                            "answer": ["Redemption: Requested -> Validated -> Fulfilled"],
                        },
                    ],
                },
            ]
        )

        model = normalize_replay_to_model(replay)
        domain_invariants = model["logical_view"]["domain_invariant_objects"]
        state_invariants = model["process_view"]["state_invariant_objects"]

        self.assertEqual(
            [item["title"] for item in domain_invariants[0]["invariant_clauses"]],
            ["Record vendor", "Record contract dates"],
        )
        self.assertEqual(
            [item["title"] for item in domain_invariants[1]["invariant_clauses"]],
            ["Provide the required details", "Provide consents"],
        )
        self.assertEqual(
            [item["title"] for item in domain_invariants[2]["invariant_clauses"]],
            ["Confirm reward eligibility", "Confirm available points"],
        )
        self.assertEqual(
            domain_invariants[2]["invariant_clauses"][0]["parent_invariant_id"],
            "domain-invariant-3",
        )
        self.assertEqual(
            [item["title"] for item in state_invariants[0]["invariant_clauses"]],
            ["Confirm reward eligibility", "Confirm available points"],
        )
