from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from afims_r.release_verification import verify_release_evidence


BASE = Path(__file__).resolve().parents[1]


class ReleaseVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((BASE / "reports" / "AFIMS_T_COMPLIANCE_REPORT.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((BASE / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))

    def test_complete_evidence_set_passes(self):
        result = verify_release_evidence(BASE, self.report, self.manifest)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["evidence_files_checked"], 85)

    def test_manifest_hash_tampering_fails(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifacts"][0]["sha256"] = "sha256:" + "0" * 64
        result = verify_release_evidence(BASE, self.report, manifest)
        self.assertEqual(result["decision"], "FAIL")
        self.assertTrue(any(item.startswith("hash:") for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
