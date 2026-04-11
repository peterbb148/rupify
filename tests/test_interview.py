"""Tests for the executable SpecOps interview harness."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from specops_tools.interview import process_round, replay_session


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

    def test_cli_accepts_piped_round_answer(self) -> None:
        """The CLI should accept answer text from stdin."""
        repo_root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            ["uv", "run", "python", "-m", "specops_tools.interview_cli", "--round", "1"],
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
                    "specops_tools.interview_replay",
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
                "specops_tools.interview_replay",
                "--input",
                str(fixture_path),
            ],
            text=True,
            capture_output=True,
            check=True,
            cwd=repo_root,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["last_round"], 6)
        self.assertEqual(payload["next_round"]["number"], 7)
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
            "IT Business Owner: Simple",
            payload["merged_answers"]["round_5"]["actor_complexity"],
        )
        self.assertIn(
            "expose/export data by API: Complex",
            payload["merged_answers"]["round_6"]["use_case_complexity"],
        )


if __name__ == "__main__":
    unittest.main()
