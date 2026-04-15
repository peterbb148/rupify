"""Tests for the deterministic UCP engine."""

from __future__ import annotations

import unittest

from rupify_tools.ucp import calculate_ucp


def build_model() -> dict[str, object]:
    """Create a representative test model.

    Returns:
        Canonical Rupify model fixture.
    """
    return {
        "project": {
            "name": "Loyalty Platform",
            "domain": "Retail",
            "problem_statement": "Legacy loyalty operations are fragmented.",
            "system_scope": "Member loyalty platform",
        },
        "actors": [
            {
                "id": "customer",
                "name": "Customer",
                "type": "human",
                "description": "Redeems rewards in the app.",
                "complexity": "complex",
            },
            {
                "id": "ops-manager",
                "name": "Operations Manager",
                "type": "human",
                "description": "Manages campaigns and reporting.",
                "complexity": "average",
            },
            {
                "id": "payment-gateway",
                "name": "Payment Gateway",
                "type": "system",
                "description": "Confirms payment completion.",
                "complexity": "simple",
            },
        ],
        "use_cases": [
            {
                "id": "uc-enroll",
                "name": "Enroll Member",
                "primary_actor": "Customer",
                "goal": "Join the loyalty program.",
                "complexity": "simple",
                "main_success_scenario": ["Customer submits enrollment.", "System creates account."],
                "extensions": [],
            },
            {
                "id": "uc-browse",
                "name": "Browse Rewards",
                "primary_actor": "Customer",
                "goal": "View available rewards.",
                "complexity": "average",
                "main_success_scenario": ["Customer opens rewards catalog."],
                "extensions": [],
            },
            {
                "id": "uc-redeem",
                "name": "Redeem Reward",
                "primary_actor": "Customer",
                "goal": "Redeem a reward.",
                "complexity": "complex",
                "main_success_scenario": ["Customer selects reward.", "System validates points."],
                "extensions": ["Reward is no longer available."],
            },
            {
                "id": "uc-catalog",
                "name": "Manage Reward Catalog",
                "primary_actor": "Operations Manager",
                "goal": "Maintain catalog items.",
                "complexity": "average",
                "main_success_scenario": ["Manager edits reward metadata."],
                "extensions": [],
            },
            {
                "id": "uc-analytics",
                "name": "Review Redemption Analytics",
                "primary_actor": "Operations Manager",
                "goal": "Inspect redemption metrics.",
                "complexity": "simple",
                "main_success_scenario": ["Manager opens dashboard."],
                "extensions": [],
            },
        ],
        "assumptions": ["Initial estimate assumes one delivery team."],
        "open_questions": ["Should partner merchants count as actors in V1?"],
        "ucp": {
            "productivity_hours_per_ucp": 20,
            "technical_factors": {
                "distributed_system": 3,
                "response_time": 3,
                "end_user_efficiency": 4,
                "complex_internal_processing": 3,
                "reusable_code": 2,
                "easy_to_install": 2,
                "easy_to_use": 4,
                "portability": 2,
                "easy_to_change": 3,
                "concurrency": 2,
                "special_security": 5,
                "third_party_access": 4,
                "special_user_training": 2,
            },
            "environmental_factors": {
                "familiar_with_process": 4,
                "application_experience": 3,
                "object_oriented_experience": 3,
                "lead_analyst_capability": 4,
                "motivation": 5,
                "stable_requirements": 3,
                "part_time_staff": 1,
                "difficult_programming_language": 2,
            },
        },
    }


class UcpTests(unittest.TestCase):
    """Coverage for UCP calculation."""

    def test_calculation_is_deterministic(self) -> None:
        """The same model should always produce the same totals."""
        result = calculate_ucp(build_model())

        self.assertEqual(result["actor_total"], 6)
        self.assertEqual(result["use_case_total"], 45)
        self.assertEqual(result["unadjusted_ucp"], 51)
        self.assertAlmostEqual(result["technical_total"], 41.0)
        self.assertAlmostEqual(result["environmental_total"], 20.5)
        self.assertAlmostEqual(result["technical_complexity_factor"], 1.01)
        self.assertAlmostEqual(result["environmental_factor"], 0.785)
        self.assertAlmostEqual(result["use_case_points"], 40.43535)
        self.assertAlmostEqual(result["effort_hours"], 808.707)

    def test_invalid_factor_value_raises(self) -> None:
        """Factor scores must remain in the valid range."""
        model = build_model()
        model["ucp"]["technical_factors"]["distributed_system"] = 9

        with self.assertRaisesRegex(ValueError, "distributed_system"):
            calculate_ucp(model)

    def test_missing_complexity_raises(self) -> None:
        """Actors and use cases must have explicit complexity."""
        model = build_model()
        model["actors"][0].pop("complexity")

        with self.assertRaisesRegex(ValueError, "missing a complexity value"):
            calculate_ucp(model)


if __name__ == "__main__":
    unittest.main()

