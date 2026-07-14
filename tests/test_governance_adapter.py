from __future__ import annotations

import json
import unittest
from pathlib import Path

from afims_r.governance_adapter import build_ci_pipeline_input, build_readiness


BASE = Path(__file__).resolve().parents[1]


class GovernanceAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compliance = json.loads((BASE / "reports" / "AFIMS_T_COMPLIANCE_REPORT.json").read_text(encoding="utf-8"))
        cls.confidence = {
            "decision": "PASS",
            "tests_1_to_13_all_yes": True,
            "test_14_no": True,
        }

    def test_local_pass_never_grants_l3(self):
        result = build_readiness(self.compliance, self.confidence, True)
        self.assertEqual(result["release_status"], "READY_FOR_CI")
        self.assertFalse(result["l3_granted"])
        self.assertEqual(result["external_gates"]["RG-027"], "NOT_EXECUTED")

    def test_failed_local_gate_blocks_ci_readiness(self):
        result = build_readiness(self.compliance, {"decision": "FAIL"}, True)
        self.assertEqual(result["release_status"], "BLOCKED")

    def test_ci_input_has_no_manual_derived_claims(self):
        result = build_ci_pipeline_input(
            "owner/repo",
            "a" * 40,
            "ghcr.io/owner/repo",
            "sha256:" + "b" * 64,
            {"afims_t": "a", "final_confidence": "b", "release_manifest": "c", "tests": "d"},
        )
        self.assertEqual(result["claimed"], {})
        self.assertNotIn("confidence", result)
        self.assertNotIn("maturity", result)
        self.assertNotIn("decision", result)

    def test_fake_commit_shape_is_rejected(self):
        with self.assertRaises(ValueError):
            build_ci_pipeline_input(
                "owner/repo",
                "not-a-real-commit",
                "ghcr.io/owner/repo",
                "sha256:" + "b" * 64,
                {"afims_t": "a", "final_confidence": "b", "release_manifest": "c", "tests": "d"},
            )

