"""Tests for the machine-oriented downstream planning export."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from rupify_tools.planning_export import build_planning_export
from tests.test_ucp import build_model


class PlanningExportTests(unittest.TestCase):
    """Coverage for the Speckify planning export contract."""

    def test_build_planning_export_flattens_ready_normative_elements_and_trace_links(self) -> None:
        """The export should flatten canonical elements and trace links into a strict contract."""
        model = build_model()
        model["model_metadata"] = {
            "semantic_id": "rupify-model",
            "change_metadata": {"semantic_hash": "abc123"},
        }
        model["requirements"] = {
            "functional_objects": [
                {
                    "id": "functional-requirement-1",
                    "semantic_id": "functional-requirement-1",
                    "statement": "Approve system changes",
                    "sub_obligations": [
                        {
                            "id": "approve-system-changes",
                            "title": "Approve system changes",
                            "summary": "Approve system changes.",
                            "acceptance": "System changes can be approved.",
                            "parent_requirement_id": "functional-requirement-1",
                            "parent_requirement_semantic_id": "functional-requirement-1",
                        }
                    ],
                    "content_semantics": "normative",
                    "readiness": {
                        "status": "ready",
                        "normative_ready": True,
                        "missing_fields": [],
                        "blocking_ambiguity_ids": [],
                    },
                    "change_metadata": {"semantic_hash": "reqhash"},
                    "trace": {"source_round": 4, "source_key": "workflow_scope"},
                }
            ],
            "non_functional_objects": [],
            "acceptance_constraint_objects": [
                {
                    "id": "acceptance-constraint-1",
                    "semantic_id": "acceptance-constraint-1",
                    "description": "SSO is required",
                    "content_semantics": "normative",
                    "readiness": {
                        "status": "partial",
                        "normative_ready": False,
                        "missing_fields": [],
                        "blocking_ambiguity_ids": ["ambiguity-open-question-1"],
                    },
                    "change_metadata": {"semantic_hash": "constrainthash"},
                    "trace": {"source_round": 2, "source_key": "constraints"},
                    "constraint_kind": "non_functional_requirement",
                    "source_requirement_id": "functional-requirement-1",
                    "linked_use_case_ids": ["uc-redeem"],
                }
            ],
        }
        model["analysis_view"] = {
            "use_cases": [
                {
                    "id": "uc-redeem",
                    "semantic_id": "uc-redeem",
                    "name": "Redeem Reward",
                    "goal": "Redeem a reward.",
                    "content_semantics": "normative",
                    "readiness": {
                        "status": "ready",
                        "normative_ready": True,
                        "missing_fields": [],
                        "blocking_ambiguity_ids": [],
                    },
                    "change_metadata": {"semantic_hash": "uchash"},
                    "trace": {"source_round": 3, "source_key": "use_cases"},
                    "main_success_scenario": ["Customer selects reward."],
                }
            ],
            "use_case_step_objects": [
                {
                    "id": "uc-redeem-step-1",
                    "semantic_id": "uc-redeem-step-1",
                    "use_case_id": "uc-redeem",
                    "step_index": 1,
                    "step_kind": "main_success",
                    "text": "Customer selects reward.",
                    "sub_actions": [
                        {
                            "id": "uc-redeem-step-1-action-1",
                            "semantic_id": "uc-redeem-step-1-action-select-reward",
                            "title": "Select reward",
                            "text": "Customer selects reward.",
                            "subject": "Customer",
                            "verb": "select",
                            "target": "reward",
                            "order_index": 1,
                            "parent_step_id": "uc-redeem-step-1",
                            "parent_step_semantic_id": "uc-redeem-step-1",
                            "parent_use_case_id": "uc-redeem",
                            "derivation_basis": "single_clause",
                        }
                    ],
                    "content_semantics": "normative",
                    "readiness": {
                        "status": "ready",
                        "normative_ready": True,
                        "missing_fields": [],
                        "blocking_ambiguity_ids": [],
                    },
                    "change_metadata": {"semantic_hash": "stephash"},
                    "trace": {"source_round": 13, "source_key": "use_case_details"},
                }
            ],
            "scenario_objects": [],
            "ambiguity_objects": [
                {
                    "id": "ambiguity-open-question-1",
                    "semantic_id": "ambiguity-open-question-1",
                    "description": "Should archived systems need approval?",
                    "content_semantics": "informative",
                    "readiness": {
                        "status": "ready",
                        "normative_ready": False,
                        "missing_fields": [],
                        "blocking_ambiguity_ids": [],
                    },
                    "change_metadata": {"semantic_hash": "ambhash"},
                    "trace": {},
                    "ambiguity_type": "open_question",
                    "resolution_status": "open",
                    "blocking_for_downstream": True,
                    "applies_to_element_ids": ["uc-redeem"],
                }
            ],
            "risk_objects": [],
            "actors": [],
        }
        model["logical_view"] = {
            "domain_entity_objects": [],
            "relationship_objects": [],
            "business_rule_objects": [],
            "domain_invariant_objects": [],
        }
        model["process_view"] = {
            "state_entity_objects": [],
            "state_transition_objects": [],
            "trigger_objects": [],
            "state_invariant_objects": [],
            "guard_condition_objects": [
                {
                    "id": "guard-condition-1",
                    "semantic_id": "guard-condition-1",
                    "name": "Payment confirmation",
                    "description": "Payment confirmation triggers redemption fulfillment",
                    "condition_text": "Payment confirmation triggers redemption fulfillment",
                    "guard_parts": [
                        {
                            "id": "guard-condition-1-part-1",
                            "semantic_id": "guard-condition-1-part-context-payment-confirmation",
                            "part_kind": "context",
                            "text": "Payment confirmation",
                            "order_index": 1,
                            "parent_guard_id": "guard-condition-1",
                            "parent_guard_semantic_id": "guard-condition-1",
                            "derivation_basis": "trigger_clause",
                        },
                        {
                            "id": "guard-condition-1-part-2",
                            "semantic_id": "guard-condition-1-part-allow-outcome-redemption-fulfillment",
                            "part_kind": "allow_outcome",
                            "text": "redemption fulfillment",
                            "order_index": 2,
                            "parent_guard_id": "guard-condition-1",
                            "parent_guard_semantic_id": "guard-condition-1",
                            "derivation_basis": "trigger_clause",
                        },
                    ],
                    "content_semantics": "normative",
                    "readiness": {
                        "status": "ready",
                        "normative_ready": True,
                        "missing_fields": [],
                        "blocking_ambiguity_ids": [],
                    },
                    "change_metadata": {"semantic_hash": "guardhash"},
                    "trace": {"source_round": 6, "source_key": "triggers_and_approvals"},
                    "state_entity_ids": [],
                    "related_transition_ids": ["state-transition-1"],
                    "source_trigger_id": "trigger-1",
                }
            ],
            "forbidden_transition_objects": [],
        }
        model["architecture_view"] = {
            "component_objects": [],
            "interface_objects": [],
            "runtime_boundary_objects": [],
        }
        model["interaction_view"] = {
            "realization_objects": [
                {
                    "id": "interaction-realization-1",
                    "semantic_id": "interaction-realization-1",
                    "use_case_name": "Redeem Reward",
                    "steps": ["Customer selects reward."],
                    "content_semantics": "informative",
                    "readiness": {
                        "status": "ready",
                        "normative_ready": False,
                        "missing_fields": [],
                        "blocking_ambiguity_ids": [],
                    },
                    "change_metadata": {"semantic_hash": "realhash"},
                    "trace": {"source_round": 3, "source_key": "use_cases"},
                }
            ],
            "message_objects": [
                {
                    "id": "interaction-message-1",
                    "semantic_id": "interaction-message-1",
                    "description": "Member App calls Rewards API",
                    "content_semantics": "informative",
                    "readiness": {
                        "status": "ready",
                        "normative_ready": False,
                        "missing_fields": [],
                        "blocking_ambiguity_ids": [],
                    },
                    "change_metadata": {"semantic_hash": "messagehash"},
                    "trace": {"source_round": 7, "source_key": "interfaces_and_integrations"},
                    "interaction_verb": "calls",
                }
            ],
        }
        model["traceability"] = {
            "requirement_to_use_case": [
                {
                    "id": "trace-req-uc-1",
                    "semantic_id": "trace-req-uc-1",
                    "from_id": "functional-requirement-1",
                    "to_id": "uc-redeem",
                    "link_type": "requirement_to_use_case",
                    "basis": "requirement statement references use-case name",
                    "change_metadata": {"semantic_hash": "tracehash"},
                }
            ],
            "ambiguity_to_element": [
                {
                    "id": "trace-ambiguity-element-1",
                    "semantic_id": "trace-ambiguity-element-1",
                    "from_id": "ambiguity-open-question-1",
                    "to_id": "uc-redeem",
                    "link_type": "ambiguity_to_element",
                    "basis": "ambiguity text explicitly references canonical element",
                    "change_metadata": {"semantic_hash": "ambtracehash"},
                }
            ],
            "artifact_lineage": [
                {
                    "id": "trace-artifact-interaction-message-1",
                    "semantic_id": "trace-artifact-interaction-message-1",
                    "from_id": "interaction-message-1",
                    "to_artifact": "interaction-model.md",
                    "artifact_section": "message flows",
                    "link_type": "artifact_lineage",
                    "basis": "canonical message flow renders into interaction-model.md",
                    "change_metadata": {"semantic_hash": "artifacthash"},
                }
            ],
        }

        export = build_planning_export(model)

        self.assertEqual(export["export_metadata"]["export_kind"], "speckify_planning_export")
        self.assertEqual(
            export["summary"]["ready_normative_ids"],
            ["functional-requirement-1", "guard-condition-1", "uc-redeem-step-1", "uc-redeem"],
        )
        self.assertEqual(export["summary"]["blocking_ambiguity_ids"], ["ambiguity-open-question-1"])
        self.assertEqual(
            next(item for item in export["elements"] if item["id"] == "ambiguity-open-question-1")[
                "change_metadata"
            ],
            {"semantic_hash": "ambhash"},
        )
        self.assertIn("acceptance-constraint-1", export["summary"]["partial_or_blocked_normative_ids"])
        self.assertTrue(any(item["family"] == "use_cases" for item in export["ready_normative_elements"]))
        self.assertTrue(any(link["family"] == "ambiguity_to_element" for link in export["trace_links"]))
        self.assertTrue(any(item["family"] == "interaction_messages" for item in export["elements"]))
        self.assertEqual(
            next(
                item for item in export["elements"] if item["id"] == "functional-requirement-1"
            )["obligations"][0]["id"],
            "approve-system-changes",
        )
        self.assertEqual(
            next(
                item for item in export["elements"] if item["id"] == "uc-redeem-step-1"
            )["sub_actions"][0]["semantic_id"],
            "uc-redeem-step-1-action-select-reward",
        )
        self.assertEqual(
            next(
                item for item in export["elements"] if item["id"] == "guard-condition-1"
            )["guard_parts"][0]["part_kind"],
            "context",
        )
        self.assertEqual(
            next(item for item in export["elements"] if item["id"] == "acceptance-constraint-1")["attributes"]["linked_use_case_ids"],
            ["uc-redeem"],
        )
        self.assertTrue(
            any(
                link["id"] == "trace-artifact-interaction-message-1"
                and link["from_id"] == "interaction-message-1"
                for link in export["trace_links"]
            )
        )

    def test_cli_writes_planning_export_json(self) -> None:
        """The planning export CLI should load a model file and write JSON output."""
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = Path(temp_dir) / "model.json"
            output_path = Path(temp_dir) / "planning-export.json"
            model_path.write_text(
                json.dumps(
                    {
                        "model_metadata": {"semantic_id": "rupify-model", "change_metadata": {}},
                        "requirements": {
                            "functional_objects": [],
                            "non_functional_objects": [],
                            "acceptance_constraint_objects": [],
                        },
                        "analysis_view": {
                            "actors": [],
                            "use_cases": [],
                            "use_case_step_objects": [],
                            "scenario_objects": [],
                            "ambiguity_objects": [],
                            "risk_objects": [],
                        },
                        "logical_view": {
                            "domain_entity_objects": [],
                            "relationship_objects": [],
                            "business_rule_objects": [],
                            "domain_invariant_objects": [],
                        },
                        "process_view": {
                            "state_entity_objects": [],
                            "state_transition_objects": [],
                            "trigger_objects": [],
                            "state_invariant_objects": [],
                            "guard_condition_objects": [],
                            "forbidden_transition_objects": [],
                        },
                        "architecture_view": {
                            "component_objects": [],
                            "interface_objects": [],
                            "runtime_boundary_objects": [],
                        },
                        "traceability": {},
                    }
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "rupify_tools.planning_export_cli",
                    "--model",
                    str(model_path),
                    "--output",
                    str(output_path),
                ],
                text=True,
                capture_output=True,
                check=True,
                cwd=repo_root,
            )

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["export_metadata"]["export_kind"], "speckify_planning_export")
            self.assertEqual(payload["summary"]["element_count"], 0)
            self.assertIn(str(output_path), completed.stdout)

    def test_checked_in_cmdb_v2_export_has_unique_ids_and_resolved_trace_references(self) -> None:
        """The checked-in CMDB V2 export should be clean for strict Speckify import."""
        repo_root = Path(__file__).resolve().parents[1]
        export_path = (
            repo_root
            / "examples"
            / "it-systems-inventory-v2"
            / "exports"
            / "speckify-planning-export.json"
        )
        payload = json.loads(export_path.read_text(encoding="utf-8"))

        element_ids = [item["id"] for item in payload["elements"]]
        self.assertEqual(len(element_ids), len(set(element_ids)))

        element_id_set = set(element_ids)
        unresolved = []
        for link in payload["trace_links"]:
            if link.get("from_id") and link["from_id"] not in element_id_set:
                unresolved.append(("from", link["id"], link["from_id"]))
            if link.get("to_id") and link["to_id"] not in element_id_set:
                unresolved.append(("to", link["id"], link["to_id"]))
        self.assertEqual(unresolved, [])
        self.assertEqual(
            next(
                item
                for item in payload["elements"]
                if item["id"] == "functional-requirement-1"
            )["obligations"][0]["id"],
            "support-stage-gates",
        )
        self.assertEqual(
            next(
                item
                for item in payload["elements"]
                if item["id"] == "functional-requirement-1"
            )["obligations"][1]["id"],
            "support-approval-states",
        )

    def test_checked_in_loyalty_v2_export_includes_step_sub_actions(self) -> None:
        """The checked-in loyalty V2 export should surface explicit step sub-actions."""
        repo_root = Path(__file__).resolve().parents[1]
        export_path = (
            repo_root
            / "examples"
            / "loyalty-platform-v2"
            / "exports"
            / "speckify-planning-export.json"
        )
        payload = json.loads(export_path.read_text(encoding="utf-8"))
        redeem_step = next(
            item for item in payload["elements"] if item["id"] == "redeem-reward-step-2"
        )
        self.assertEqual(
            [item["id"] for item in redeem_step["sub_actions"]],
            [
                "redeem-reward-step-2-action-1",
                "redeem-reward-step-2-action-2",
            ],
        )
        self.assertEqual(
            [item["title"] for item in redeem_step["sub_actions"]],
            ["Validate reward eligibility", "Validate available points"],
        )
        self.assertEqual(
            redeem_step["sub_actions"][0]["derivation_basis"],
            "shared_verb_objects",
        )

    def test_checked_in_loyalty_v2_export_includes_guard_parts(self) -> None:
        """The checked-in loyalty V2 export should surface explicit guard parts."""
        repo_root = Path(__file__).resolve().parents[1]
        export_path = (
            repo_root
            / "examples"
            / "loyalty-platform-v2"
            / "exports"
            / "speckify-planning-export.json"
        )
        payload = json.loads(export_path.read_text(encoding="utf-8"))
        guard = next(
            item for item in payload["elements"] if item["id"] == "guard-condition-2"
        )
        self.assertEqual(
            [item["part_kind"] for item in guard["guard_parts"]],
            ["condition", "allow_outcome", "block_outcome"],
        )
        self.assertEqual(
            guard["guard_parts"][0]["derivation_basis"],
            "required_before_clause",
        )

    def test_checked_in_loyalty_v2_export_includes_expanded_requirement_obligations(self) -> None:
        """The checked-in loyalty V2 export should include broader requirement clause structure."""
        repo_root = Path(__file__).resolve().parents[1]
        export_path = (
            repo_root
            / "examples"
            / "loyalty-platform-v2"
            / "exports"
            / "speckify-planning-export.json"
        )
        payload = json.loads(export_path.read_text(encoding="utf-8"))
        requirement = next(
            item for item in payload["elements"] if item["id"] == "non_functional-requirement-3"
        )
        self.assertEqual(
            [item["title"] for item in requirement["obligations"]],
            [
                "Support integration with external systems with payment confirmation",
                "Support integration with external systems with reporting sources",
            ],
        )


if __name__ == "__main__":
    unittest.main()
