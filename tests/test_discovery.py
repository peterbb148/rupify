"""Tests for deterministic interview-to-model normalization."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from specops_tools.discovery import normalize_replay_to_model
from specops_tools.interview import replay_session


class DiscoveryTests(unittest.TestCase):
    """Coverage for interview normalization."""

    def test_normalize_replay_to_model_maps_new_view_sections(self) -> None:
        """Replay answers for the new rounds should land in the matching model sections."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "SpecOps Test"},
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

        self.assertEqual(model["project"]["name"], "SpecOps Test")
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

    def test_normalize_replay_to_model_keeps_empty_sections_explicit(self) -> None:
        """Missing optional view rounds should still produce stable empty sections."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "SpecOps Test"},
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
        self.assertEqual(model["actors"], [])
        self.assertEqual(model["use_cases"], [])

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
        self.assertEqual(model["actors"][0]["type"], "human")
        self.assertEqual(model["actors"][0]["model_layer"], "analysis")
        self.assertEqual(model["actors"][0]["interaction_style"], "user_interface")
        self.assertEqual(model["actors"][0]["responsibilities"], [])
        self.assertEqual(model["actors"][0]["trace"]["source_round"], 3)
        self.assertEqual(model["actors"][1]["type"], "system")
        self.assertEqual(model["actors"][1]["interaction_style"], "system_interface")
        self.assertEqual(model["actors"][2]["type"], "system")
        self.assertEqual(model["use_cases"][0]["id"], "browse-rewards")
        self.assertEqual(model["use_cases"][0]["goal"], "Browse Rewards")
        self.assertEqual(model["use_cases"][0]["model_layer"], "analysis")
        self.assertEqual(model["use_cases"][0]["primary_actor_id"], "")
        self.assertEqual(model["use_cases"][0]["supporting_actor_ids"], [])
        self.assertEqual(model["use_cases"][0]["trigger"], "")
        self.assertEqual(model["use_cases"][0]["preconditions"], [])
        self.assertEqual(model["use_cases"][0]["postconditions"], [])
        self.assertEqual(model["use_cases"][0]["trace"]["source_key"], "use_cases")
        self.assertEqual(model["use_cases"][1]["complexity"], "unclassified")
        self.assertEqual(model["analysis_view"]["actor_ids"][0], "operations-manager")
        self.assertEqual(model["analysis_view"]["use_case_ids"][0], "browse-rewards")
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
                        {"key": "integrations", "answer": "System API"},
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
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "components_and_services", "answer": ["System API"]},
                        {"key": "interfaces_and_integrations", "answer": ["Portal calls System API"]},
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
            model["traceability"]["use_case_to_analysis"][0]["to_id"],
            "entity-system",
        )
        self.assertEqual(
            model["traceability"]["analysis_to_design"][0]["to_id"],
            "component-system-api",
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
        self.assertEqual(model["logical_view"]["domain_entities"], [])
        self.assertEqual(model["logical_view"]["relationship_objects"], [])
        self.assertEqual(model["process_view"]["state_entities"], [])

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
