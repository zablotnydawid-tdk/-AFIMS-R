from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from afims_r.final_confidence import evaluate_final_confidence


BASE = Path(__file__).resolve().parents[1]


class FinalConfidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((BASE / "reports" / "AFIMS_T_COMPLIANCE_REPORT.json").read_text(encoding="utf-8"))
        cls.results = json.loads((BASE / "reports" / "AFIMS_T_CASE_RESULTS.json").read_text(encoding="utf-8"))["results"]

    def test_complete_reference_pack_passes_14_questions(self):
        result = evaluate_final_confidence(self.report, self.results)
        self.assertEqual(result["decision"], "PASS")
        self.assertTrue(result["tests_1_to_13_all_yes"])
        self.assertTrue(result["test_14_no"])
        self.assertEqual(result["test_14_method"]["findings"], [])
        self.assertFalse(result["test_14_method"]["exhaustive_outside_declared_scope"])

    def test_group_failure_blocks_final_confidence(self):
        report = copy.deepcopy(self.report)
        report["groups"]["T3"]["decision"] = "FAIL"
        self.assertEqual(evaluate_final_confidence(report, self.results)["decision"], "FAIL")

    def test_missing_evidence_blocks_traceability(self):
        results = copy.deepcopy(self.results)
        results[0]["evidence_hash_valid"] = False
        outcome = evaluate_final_confidence(self.report, results)
        self.assertFalse(outcome["questions"][10]["passed"])
        self.assertIn("EVIDENCE_OR_EXECUTION_IMPROVEMENT_REQUIRED", outcome["test_14_method"]["findings"])
        self.assertEqual(outcome["decision"], "FAIL")
