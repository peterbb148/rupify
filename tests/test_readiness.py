"""Tests for readiness and staleness reporting."""

from __future__ import annotations

import unittest

from specops_tools.readiness import (
    evaluate_readiness,
    evaluate_readiness_details,
    evaluate_traceability,
    identify_stale_artifacts,
)


class ReadinessTests(unittest.TestCase):
    """Coverage for interview-state readiness helpers."""

    def test_evaluate_readiness_reports_partial_and_ready_views(self) -> None:
        """Readiness should distinguish complete, partial, and blocked views."""
        readiness = evaluate_readiness(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Inventory system"},
                        {"key": "problem", "answer": "Poor visibility"},
                        {"key": "in_scope", "answer": "Non-OT"},
                    ],
                },
                {
                    "round": 2,
                    "responses": [
                        {"key": "outcomes", "answer": "Better planning"},
                    ],
                },
                {
                    "round": 3,
                    "responses": [
                        {"key": "actors", "answer": "Architect"},
                        {"key": "use_cases", "answer": "Search systems"},
                    ],
                },
                {
                    "round": 4,
                    "responses": [
                        {"key": "workflow_scope", "answer": "Edit metadata"},
                    ],
                },
                {
                    "round": 5,
                    "responses": [
                        {"key": "domain_entities", "answer": "System"},
                    ],
                },
                {
                    "round": 6,
                    "responses": [
                        {"key": "state_entities", "answer": "System lifecycle"},
                        {"key": "states_and_transitions", "answer": "Proposed -> Active"},
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "components_and_services", "answer": "Web app"},
                        {"key": "interfaces_and_integrations", "answer": "Web app calls API"},
                    ],
                },
                {
                    "round": 8,
                    "responses": [
                        {"key": "actor_complexity", "answer": "Architect: complex"},
                    ],
                },
            ]
        )

        self.assertEqual(readiness["discovery"], "ready")
        self.assertEqual(readiness["use_case"], "ready")
        self.assertEqual(readiness["logical"], "partial")
        self.assertEqual(readiness["process"], "ready")
        self.assertEqual(readiness["architecture"], "ready")
        self.assertEqual(readiness["ucp"], "partial")

    def test_evaluate_readiness_details_reports_missing_gate_fields(self) -> None:
        """Detailed readiness should expose the specific missing keys per view."""
        details = evaluate_readiness_details(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Inventory system"},
                        {"key": "problem", "answer": "Poor visibility"},
                    ],
                },
                {
                    "round": 5,
                    "responses": [
                        {"key": "domain_entities", "answer": "System"},
                        {"key": "business_rules", "answer": "Owner required"},
                    ],
                },
            ]
        )

        self.assertEqual(details["discovery"]["status"], "partial")
        self.assertEqual(details["discovery"]["required_missing"], ["in_scope", "outcomes"])
        self.assertEqual(details["logical"]["status"], "partial")
        self.assertEqual(details["logical"]["required_missing"], ["relationships"])
        self.assertEqual(details["logical"]["supporting_present"], ["business_rules"])

    def test_identify_stale_artifacts_maps_round_updates_to_outputs(self) -> None:
        """Updated rounds should mark only dependent artifacts stale."""
        stale = identify_stale_artifacts(
            [
                {"round": 2, "responses": [{"key": "constraints", "answer": "Web UI"}]},
                {"round": 9, "responses": [{"key": "use_case_complexity", "answer": "Search: average"}]},
            ]
        )

        self.assertEqual(
            stale,
            ["requirements-spec.md", "ucp-estimate.md"],
        )

    def test_identify_stale_artifacts_marks_state_model_for_process_updates(self) -> None:
        """Process-view updates should mark the formal state-model artifact stale."""
        stale = identify_stale_artifacts(
            [
                {
                    "round": 6,
                    "responses": [
                        {
                            "key": "states_and_transitions",
                            "answer": "Draft -> Submitted -> Approved",
                        }
                    ],
                }
            ]
        )

        self.assertEqual(
            stale,
            ["requirements-spec.md", "state-model.md", "use-case-model.md"],
        )

    def test_identify_stale_artifacts_marks_domain_model_for_logical_updates(self) -> None:
        """Logical-view updates should mark the formal domain-model artifact stale."""
        stale = identify_stale_artifacts(
            [
                {
                    "round": 5,
                    "responses": [
                        {"key": "relationships", "answer": "A Member redeems Rewards"},
                    ],
                }
            ]
        )

        self.assertEqual(
            stale,
            ["domain-model.md", "requirements-spec.md"],
        )

    def test_identify_stale_artifacts_marks_interaction_model_for_use_case_and_architecture_updates(self) -> None:
        """Use-case or architecture updates should mark the formal interaction-model artifact stale."""
        stale = identify_stale_artifacts(
            [
                {
                    "round": 3,
                    "responses": [
                        {"key": "use_cases", "answer": "Redeem Reward"},
                    ],
                },
                {
                    "round": 7,
                    "responses": [
                        {"key": "interfaces_and_integrations", "answer": "Member App calls Rewards API"},
                    ],
                },
            ]
        )

        self.assertEqual(
            stale,
            [
                "deployment-model.md",
                "interaction-model.md",
                "requirements-spec.md",
                "use-case-model.md",
            ],
        )

    def test_identify_stale_artifacts_marks_deployment_model_for_architecture_updates(self) -> None:
        """Architecture updates should mark the formal deployment-model artifact stale."""
        stale = identify_stale_artifacts(
            [
                {
                    "round": 7,
                    "responses": [
                        {"key": "runtime_boundaries", "answer": "Rewards API runs separately from the UI"},
                    ],
                },
            ]
        )

        self.assertEqual(
            stale,
            [
                "deployment-model.md",
                "interaction-model.md",
                "requirements-spec.md",
                "use-case-model.md",
            ],
        )

    def test_evaluate_traceability_reports_missing_links(self) -> None:
        """Trace validation should identify missing links by family."""
        model = {
            "requirements": {
                "functional_objects": [
                    {"id": "functional-requirement-1"},
                    {"id": "functional-requirement-2"},
                ]
            },
            "use_cases": [
                {"id": "approve-system"},
                {"id": "search-systems"},
            ],
            "logical_view": {"domain_entity_objects": [{"id": "entity-system"}]},
            "process_view": {"state_entity_objects": []},
            "architecture_view": {"component_objects": [{"id": "component-system-api"}]},
            "traceability": {
                "requirement_to_use_case": [
                    {"from_id": "functional-requirement-1", "to_id": "approve-system"}
                ],
                "use_case_to_analysis": [],
                "analysis_to_design": [],
            },
        }

        validation = evaluate_traceability(model)

        self.assertEqual(validation["requirement_to_use_case"]["status"], "partial")
        self.assertEqual(
            validation["requirement_to_use_case"]["missing_from_ids"],
            ["functional-requirement-2"],
        )
        self.assertEqual(validation["use_case_to_analysis"]["status"], "blocked")
        self.assertEqual(
            validation["use_case_to_analysis"]["missing_from_ids"],
            ["approve-system", "search-systems"],
        )
        self.assertEqual(validation["analysis_to_design"]["status"], "blocked")
        self.assertEqual(
            validation["analysis_to_design"]["missing_from_ids"],
            ["entity-system"],
        )
