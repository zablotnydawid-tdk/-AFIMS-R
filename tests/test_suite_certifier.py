from __future__ import annotations

import unittest

from afims_r.suite_certifier import IndependentSuiteCertifier


class SuiteCertifierTests(unittest.TestCase):
    def base(self):
        manifest = {
            "expected_case_count": 1,
            "case_ids": ["T1.01"],
            "actors": {"generator": "g", "validator": "v", "certifier": "c"},
        }
        results = [{"test_id": "T1.01", "suite_expectation_met": True, "unresolved": 0}]
        evidence = {"valid_evidence_count": 1, "invalid_hash_count": 0}
        return manifest, results, evidence

    def test_complete_suite_passes(self):
        decision = IndependentSuiteCertifier().certify(*self.base())
        self.assertEqual(decision.decision, "PASS")

    def test_incomplete_suite_fails(self):
        manifest, _, evidence = self.base()
        decision = IndependentSuiteCertifier().certify(manifest, [], evidence)
        self.assertEqual(decision.decision, "FAIL")

    def test_generator_self_certification_fails(self):
        manifest, results, evidence = self.base()
        manifest["actors"]["generator"] = IndependentSuiteCertifier.identity
        decision = IndependentSuiteCertifier().certify(manifest, results, evidence)
        self.assertEqual(decision.decision, "FAIL")

    def test_validator_certifier_collision_fails(self):
        manifest, results, evidence = self.base()
        manifest["actors"]["validator"] = IndependentSuiteCertifier.identity
        decision = IndependentSuiteCertifier().certify(manifest, results, evidence)
        self.assertEqual(decision.decision, "FAIL")

    def test_failed_expectation_blocks(self):
        manifest, results, evidence = self.base()
        results[0]["suite_expectation_met"] = False
        decision = IndependentSuiteCertifier().certify(manifest, results, evidence)
        self.assertEqual(decision.decision, "FAIL")

    def test_unresolved_blocks(self):
        manifest, results, evidence = self.base()
        results[0]["unresolved"] = 1
        decision = IndependentSuiteCertifier().certify(manifest, results, evidence)
        self.assertEqual(decision.decision, "FAIL")

    def test_missing_evidence_blocks(self):
        manifest, results, evidence = self.base()
        evidence["valid_evidence_count"] = 0
        decision = IndependentSuiteCertifier().certify(manifest, results, evidence)
        self.assertEqual(decision.decision, "FAIL")

    def test_invalid_hash_blocks(self):
        manifest, results, evidence = self.base()
        evidence["invalid_hash_count"] = 1
        decision = IndependentSuiteCertifier().certify(manifest, results, evidence)
        self.assertEqual(decision.decision, "FAIL")

