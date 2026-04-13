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
        self.assertIn("System", model["logical_view"]["domain_entities"])
        self.assertEqual(
            model["logical_view"]["domain_entity_objects"][0]["id"],
            "entity-system",
        )
        self.assertIn(
            "Draft -> Submitted -> Approved",
            model["process_view"]["states_and_transitions"],
        )
        self.assertEqual(
            model["process_view"]["state_entity_objects"][0]["id"],
            "state-entity-approval-request",
        )
        self.assertIn("Web app", model["architecture_view"]["components_and_services"])
        self.assertEqual(
            model["architecture_view"]["component_objects"][0]["id"],
            "component-web-app",
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
        self.assertEqual(model["logical_view"]["domain_entities"], [])
        self.assertEqual(model["logical_view"]["relationship_objects"], [])
        self.assertEqual(model["process_view"]["state_entities"], [])
        self.assertEqual(model["architecture_view"]["runtime_boundary_objects"], [])
