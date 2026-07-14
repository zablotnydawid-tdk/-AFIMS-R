from __future__ import annotations

import json
import unittest
from pathlib import Path

from afims_r.fixture_evaluator import evaluate_fixture


BASE = Path(__file__).resolve().parents[1]
SUITE = json.loads((BASE / "fixtures" / "afims_t_cases.json").read_text(encoding="utf-8"))


class AFIMSTExecutableFixtures(unittest.TestCase):
    pass


def make_test(case):
    def test(self):
        result = evaluate_fixture(case)
        self.assertEqual(
            result["observed_validator_decision"],
            case["expected_validator_decision"],
            msg=json.dumps(result, ensure_ascii=False, indent=2),
        )
        self.assertEqual(result["unresolved"], 0)
    return test


for fixture in SUITE["cases"]:
    method_name = "test_" + fixture["test_id"].replace(".", "_")
    setattr(AFIMSTExecutableFixtures, method_name, make_test(fixture))


if __name__ == "__main__":
    unittest.main()

