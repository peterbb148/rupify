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
                    "text": "Customer selects reward.",
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
            "guard_condition_objects": [],
            "forbidden_transition_objects": [],
        }
        model["architecture_view"] = {
            "component_objects": [],
            "interface_objects": [],
            "runtime_boundary_objects": [],
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
        }

        export = build_planning_export(model)

        self.assertEqual(export["export_metadata"]["export_kind"], "speckify_planning_export")
        self.assertEqual(
            export["summary"]["ready_normative_ids"],
            ["functional-requirement-1", "uc-redeem-step-1", "uc-redeem"],
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
        self.assertEqual(
            next(item for item in export["elements"] if item["id"] == "acceptance-constraint-1")["attributes"]["linked_use_case_ids"],
            ["uc-redeem"],
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


if __name__ == "__main__":
    unittest.main()
