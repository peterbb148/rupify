"""Tests for the executable Rupify interview harness."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from rupify_tools.interview import (
    get_round,
    merge_round_inputs,
    process_round,
    replay_session,
    replay_session_with_updates,
)


class InterviewHarnessTests(unittest.TestCase):
    """Coverage for interview automation helpers."""

    def test_process_round_parses_round_one_block(self) -> None:
        """Round 1 answers should parse into a structured mapping."""
        result = process_round(
            1,
            (
                "Idea: IT systems inventory\n"
                "Problem: overlapping tools\n"
                "Users: IT Business Owners\n"
                "In scope: all non-OT systems\n"
                "Out of scope: OT systems\n"
            ),
        )

        self.assertEqual(result["parsed_answers"]["idea"], "IT systems inventory")
        self.assertEqual(result["parsed_answers"]["problem"], "overlapping tools")
        self.assertEqual(result["next_round"]["number"], 2)

    def test_replay_session_merges_round_outputs(self) -> None:
        """Replay should preserve per-round parsed answers and the next round."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "answer": (
                        "Idea: Inventory system\n"
                        "Problem: poor visibility\n"
                        "Users: Architects\n"
                        "In scope: non-OT\n"
                        "Out of scope: OT\n"
                    ),
                },
                {
                    "round": 2,
                    "answer": (
                        "Outcomes: better planning\n"
                        "Success criteria: one inventory source\n"
                        "Required data: all metadata\n"
                        "Constraints: web UI\n"
                    ),
                },
            ]
        )

        self.assertEqual(replay["last_round"], 2)
        self.assertEqual(replay["merged_answers"]["round_1"]["users"], "Architects")
        self.assertEqual(replay["next_round"]["number"], 3)
        self.assertEqual(replay["readiness"]["discovery"], "ready")
        self.assertEqual(replay["readiness"]["use_case"], "blocked")
        self.assertEqual(replay["readiness"]["logical"], "blocked")
        self.assertEqual(replay["readiness"]["process"], "blocked")
        self.assertEqual(replay["readiness"]["architecture"], "blocked")
        self.assertEqual(replay["readiness_details"]["discovery"]["required_missing"], [])
        self.assertEqual(replay["traceability_validation"]["requirement_to_use_case"]["status"], "blocked")
        self.assertEqual(
            replay["element_readiness_validation"]["summary"]["ready_normative_ids"],
            [
                "non_functional-requirement-1",
                "acceptance-constraint-requirement-1",
                "acceptance-constraint-success-1",
            ],
        )
        self.assertEqual(replay["stale_artifacts"], [])

    def test_replay_session_accepts_individual_question_responses(self) -> None:
        """Replay should support storing answers per question instead of per round block."""
        replay = replay_session(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Inventory system"},
                        {"key": "problem", "answer": "Poor visibility"},
                        {"key": "users", "answer": "Architects"},
                        {"key": "in_scope", "answer": "Non-OT"},
                        {"key": "out_of_scope", "answer": "OT"},
                    ],
                }
            ]
        )

        self.assertEqual(replay["last_round"], 1)
        self.assertEqual(
            replay["transcript"][0]["responses"][0]["answer"],
            "Inventory system",
        )
        self.assertEqual(replay["merged_answers"]["round_1"]["problem"], "Poor visibility")
        self.assertEqual(replay["next_round"]["number"], 2)

    def test_merge_round_inputs_updates_only_targeted_response(self) -> None:
        """A targeted response update should merge into one round without dropping siblings."""
        merged = merge_round_inputs(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Inventory system"},
                        {"key": "problem", "answer": "Poor visibility"},
                        {"key": "users", "answer": "Architects"},
                    ],
                }
            ],
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "problem", "answer": "Poor visibility across regions"},
                    ],
                }
            ],
        )

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["round"], 1)
        responses = {item["key"]: item["answer"] for item in merged[0]["responses"]}
        self.assertEqual(responses["idea"], "Inventory system")
        self.assertEqual(responses["users"], "Architects")
        self.assertEqual(responses["problem"], "Poor visibility across regions")

    def test_replay_session_with_updates_can_extend_existing_session(self) -> None:
        """Replaying with updates should preserve prior rounds and add the new answers."""
        replay = replay_session_with_updates(
            [
                {
                    "round": 1,
                    "responses": [
                        {"key": "idea", "answer": "Inventory system"},
                        {"key": "problem", "answer": "Poor visibility"},
                        {"key": "users", "answer": "Architects"},
                        {"key": "in_scope", "answer": "Non-OT"},
                        {"key": "out_of_scope", "answer": "OT"},
                    ],
                }
            ],
            [
                {
                    "round": 2,
                    "responses": [
                        {"key": "outcomes", "answer": "Better planning"},
                        {"key": "success_criteria", "answer": "One inventory source"},
                    ],
                }
            ],
        )

        self.assertEqual(replay["last_round"], 2)
        self.assertEqual(replay["merged_answers"]["round_1"]["idea"], "Inventory system")
        self.assertEqual(replay["merged_answers"]["round_2"]["outcomes"], "Better planning")
        self.assertEqual(replay["next_round"]["number"], 3)
        self.assertEqual(len(replay["merged_round_inputs"]), 2)
        self.assertEqual(replay["readiness"]["discovery"], "ready")
        self.assertEqual(replay["readiness_details"]["discovery"]["status"], "ready")
        self.assertEqual(replay["traceability_validation"]["requirement_to_use_case"]["status"], "blocked")
        self.assertEqual(replay["stale_artifacts"], ["requirements-spec.md", "system-document.md"])

    def test_cli_accepts_piped_round_answer(self) -> None:
        """The CLI should accept answer text from stdin."""
        repo_root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            ["uv", "run", "python", "-m", "rupify_tools.interview_cli", "--round", "1"],
            input=(
                "Idea: IT systems inventory\n"
                "Problem: duplicate systems\n"
                "Users: IT Business Owners\n"
                "In scope: all non-OT systems\n"
                "Out of scope: OT systems\n"
            ),
            text=True,
            capture_output=True,
            check=True,
            cwd=repo_root,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["parsed_answers"]["idea"], "IT systems inventory")
        self.assertEqual(payload["next_round"]["number"], 2)

    def test_domain_round_exposes_logical_view_guidance(self) -> None:
        """Round 5 should gather logical-view concepts without forcing technical design language."""
        round_definition = get_round(5)

        self.assertIn(
            "Focus on the important nouns, relationships, and rules, not implementation classes.",
            round_definition.guidance,
        )
        self.assertEqual(round_definition.questions[0].key, "domain_entities")
        self.assertIn("Capability", round_definition.questions[0].example)
        self.assertEqual(round_definition.questions[1].key, "relationships")
        self.assertEqual(round_definition.questions[2].key, "business_rules")

    def test_state_round_exposes_process_view_guidance(self) -> None:
        """Round 6 should gather process-view behavior without forcing implementation events."""
        round_definition = get_round(6)

        self.assertIn(
            "Focus on business lifecycle behavior, approvals, and transitions, not implementation events.",
            round_definition.guidance,
        )
        self.assertEqual(round_definition.questions[0].key, "state_entities")
        self.assertIn("Approval request", round_definition.questions[0].example)
        self.assertEqual(round_definition.questions[1].key, "states_and_transitions")
        self.assertEqual(round_definition.questions[2].key, "triggers_and_approvals")

    def test_architecture_round_exposes_view_guidance(self) -> None:
        """Round 7 should gather architectural structure without collapsing into implementation detail."""
        round_definition = get_round(7)

        self.assertIn(
            "Focus on business-relevant components and boundaries, not low-level implementation classes.",
            round_definition.guidance,
        )
        self.assertEqual(round_definition.questions[0].key, "components_and_services")
        self.assertIn("Workflow service", round_definition.questions[0].example)
        self.assertEqual(round_definition.questions[1].key, "interfaces_and_integrations")
        self.assertEqual(round_definition.questions[2].key, "runtime_boundaries")

    def test_risk_round_exposes_template_driven_risk_guidance(self) -> None:
        """Round 12 should capture explicit risks for the document suite."""
        round_definition = get_round(12)

        self.assertIn(
            "Capture the major project or system risks that should appear in the document set.",
            round_definition.prompt,
        )
        self.assertEqual(round_definition.questions[0].key, "risks")
        self.assertIn("priority: high", round_definition.questions[0].example)

    def test_use_case_detail_round_exposes_scenario_and_ui_fields(self) -> None:
        """Round 13 should gather use-case detail, scenarios, and UI notes."""
        round_definition = get_round(13)

        self.assertEqual(round_definition.questions[0].key, "use_case_details")
        self.assertEqual(round_definition.questions[1].key, "scenarios")
        self.assertEqual(round_definition.questions[2].key, "ui_notes")
        self.assertIn("flow:", round_definition.questions[0].example)
        self.assertIn("Only add UI notes", round_definition.guidance[1])

    def test_ucp_actor_round_exposes_inversion_guidance(self) -> None:
        """Round 8 should explain the common actor complexity intuition mismatch."""
        round_definition = get_round(8)

        self.assertIn(
            "System or API actors are usually simpler than humans using a rich UI.",
            round_definition.guidance,
        )
        question = round_definition.questions[0]
        self.assertIn("`simple` usually means a system or API actor.", question.guidance)
        self.assertIn("Enterprise architect: complex", question.example)

    def test_technical_factor_round_exposes_0_to_5_guidance(self) -> None:
        """Round 10 should clarify that the factor scale is about influence, not quality."""
        result = process_round(
            10,
            (
                "Technical:\n"
                "security: 5\n"
                "third-party access: 4\n"
                "ease of change: 4\n"
            ),
        )

        self.assertIn(
            "Use a 0-5 influence scale, not a good-versus-bad scale.",
            result["round"]["guidance"],
        )
        self.assertIn(
            "Score how strongly the factor shapes the system, not whether the team is performing well.",
            result["round"]["guidance"],
        )
        self.assertIn(
            "Security and third-party access are often high for internal enterprise systems.",
            result["round"]["questions"][0]["guidance"],
        )
        self.assertIn("security: 5", result["round"]["questions"][0]["example"])

    def test_replay_cli_reads_fixture(self) -> None:
        """The replay CLI should process a fixture file."""
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_path = Path(temp_dir) / "session.json"
            fixture_path.write_text(
                json.dumps(
                    {
                        "rounds": [
                            {
                                "round": 1,
                                "answer": (
                                    "Idea: Inventory system\n"
                                    "Problem: poor visibility\n"
                                    "Users: Architects\n"
                                    "In scope: non-OT\n"
                                    "Out of scope: OT\n"
                                ),
                            }
                        ]
                    }
                )
            )

            completed = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "rupify_tools.interview_replay",
                    "--input",
                    str(fixture_path),
                ],
                text=True,
                capture_output=True,
                check=True,
                cwd=repo_root,
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["last_round"], 1)
        self.assertEqual(payload["next_round"]["number"], 2)

    def test_replay_cli_replays_it_systems_inventory_session(self) -> None:
        """The checked-in dogfooding interview fixture should replay cleanly."""
        repo_root = Path(__file__).resolve().parents[1]
        fixture_path = repo_root / "tests" / "fixtures" / "it_systems_inventory_session.json"

        completed = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "rupify_tools.interview_replay",
                "--input",
                str(fixture_path),
            ],
            text=True,
            capture_output=True,
            check=True,
            cwd=repo_root,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["last_round"], 11)
        self.assertEqual(payload["next_round"]["number"], 12)
        self.assertEqual(
            payload["transcript"][0]["responses"][0]["label"],
            "Idea",
        )
        self.assertEqual(
            payload["merged_answers"]["round_1"]["idea"],
            "A system to manage inventory of IT Systems themselves.",
        )
        self.assertEqual(
            payload["merged_answers"]["round_1"]["out_of_scope"],
            "OT system.",
        )
        self.assertEqual(
            payload["merged_answers"]["round_2"]["constraints"],
            "UI must be web based",
        )
        self.assertIn(
            "Business owners",
            payload["merged_answers"]["round_3"]["actors"],
        )
        self.assertIn(
            "System name",
            payload["merged_answers"]["round_4"]["metadata_fields"],
        )
        self.assertIn(
            "Business owners: Complex",
            payload["merged_answers"]["round_8"]["actor_complexity"],
        )
        self.assertIn(
            "report portfolio gaps: Average",
            payload["merged_answers"]["round_9"]["use_case_complexity"],
        )
        self.assertEqual(payload["readiness"]["logical"], "ready")
        self.assertEqual(payload["readiness"]["process"], "ready")
        self.assertEqual(payload["readiness"]["architecture"], "ready")
        self.assertEqual(payload["readiness"]["ucp"], "ready")
        self.assertEqual(payload["readiness_details"]["logical"]["required_missing"], [])
        self.assertEqual(payload["traceability_validation"]["artifact_lineage"]["status"], "ready")

    def test_interview_to_formal_cli_renders_formal_artifacts_from_fixture(self) -> None:
        """The direct interview-to-formal CLI should render the formal artifact family."""
        repo_root = Path(__file__).resolve().parents[1]
        fixture_path = repo_root / "tests" / "fixtures" / "it_systems_inventory_session.json"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "formal-out"
            model_path = Path(temp_dir) / "rupify-model.json"

            completed = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "rupify_tools.interview_to_formal_cli",
                    "--input",
                    str(fixture_path),
                    "--output-dir",
                    str(output_dir),
                    "--write-model",
                    str(model_path),
                ],
                text=True,
                capture_output=True,
                check=True,
                cwd=repo_root,
            )

            self.assertIn("domain-model.md", completed.stdout)
            self.assertTrue((output_dir / "requirements-spec.md").exists())
            self.assertTrue((output_dir / "use-case-model.md").exists())
            self.assertTrue((output_dir / "use-case-documents.md").exists())
            self.assertTrue((output_dir / "scenario-documents.md").exists())
            self.assertTrue((output_dir / "domain-model.md").exists())
            self.assertTrue((output_dir / "interaction-model.md").exists())
            self.assertTrue((output_dir / "deployment-model.md").exists())
            self.assertTrue((output_dir / "state-model.md").exists())
            self.assertFalse((output_dir / "ucp-estimate.md").exists())
            self.assertTrue(model_path.exists())

    def test_replay_cli_applies_updates_fixture(self) -> None:
        """The replay CLI should support targeted updates without replay restarts."""
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_path = Path(temp_dir) / "session.json"
            updates_path = Path(temp_dir) / "updates.json"
            fixture_path.write_text(
                json.dumps(
                    {
                        "rounds": [
                            {
                                "round": 1,
                                "responses": [
                                    {"key": "idea", "answer": "Inventory system"},
                                    {"key": "problem", "answer": "Poor visibility"},
                                    {"key": "users", "answer": "Architects"},
                                    {"key": "in_scope", "answer": "Non-OT"},
                                    {"key": "out_of_scope", "answer": "OT"},
                                ],
                            }
                        ]
                    }
                )
            )
            updates_path.write_text(
                json.dumps(
                    {
                        "rounds": [
                            {
                                "round": 1,
                                "responses": [
                                    {
                                        "key": "problem",
                                        "answer": "Poor visibility across regions",
                                    }
                                ],
                            },
                            {
                                "round": 2,
                                "responses": [
                                    {"key": "outcomes", "answer": "Better planning"},
                                ],
                            },
                        ]
                    }
                )
            )

            completed = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "rupify_tools.interview_replay",
                    "--input",
                    str(fixture_path),
                    "--updates",
                    str(updates_path),
                ],
                text=True,
                capture_output=True,
                check=True,
                cwd=repo_root,
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["merged_answers"]["round_1"]["problem"], "Poor visibility across regions")
        self.assertEqual(payload["merged_answers"]["round_2"]["outcomes"], "Better planning")
        self.assertEqual(payload["next_round"]["number"], 3)
        self.assertEqual(payload["readiness"]["discovery"], "ready")
        self.assertEqual(payload["readiness_details"]["discovery"]["required_missing"], [])
        self.assertEqual(payload["traceability_validation"]["requirement_to_use_case"]["status"], "blocked")
        self.assertEqual(payload["stale_artifacts"], ["requirements-spec.md", "system-document.md"])


if __name__ == "__main__":
    unittest.main()
