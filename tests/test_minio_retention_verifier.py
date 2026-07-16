from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
SCRIPT = BASE / "governance" / "release-governance-v3.2" / "scripts" / "verify-minio-retention.sh"
SUCCESS_FIXTURE = BASE / "governance" / "release-governance-v3.2" / "tests" / "retention-success.json"


class MinioRetentionVerifierTests(unittest.TestCase):
    def run_verifier(
        self,
        *,
        stat_json: str | dict,
        retention_json: str | dict,
        readback: bytes = b"release-decision",
        expected: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "readback.bin"
            source.write_bytes(readback)
            calls = root / "calls.log"
            evidence = root / "evidence.json"
            fake_bin = root / "bin"
            fake_bin.mkdir()
            mc = fake_bin / "mc"
            mc.write_text(
                textwrap.dedent(
                    """#!/usr/bin/env bash
                    set -euo pipefail
                    printf '%s\\n' "$*" >> "$MC_CALLS"
                    if [[ "$1" == "stat" ]]; then
                      printf '%s\\n' "$MC_STAT_JSON"
                      exit 0
                    fi
                    if [[ "$1" == "retention" && "$2" == "info" ]]; then
                      if [[ "$5" != "test-version" ]]; then
                        echo "wrong version for retention" >&2
                        exit 12
                      fi
                      printf '%s\\n' "$MC_RETENTION_JSON"
                      exit 0
                    fi
                    if [[ "$1" == "cp" ]]; then
                      if [[ "$3" != "test-version" ]]; then
                        echo "wrong version for cp" >&2
                        exit 13
                      fi
                      cp "$MC_READBACK_FILE" "$5"
                      exit 0
                    fi
                    echo "unexpected mc args: $*" >&2
                    exit 99
                    """
                ).strip()
                + "\n"
            )
            mc.chmod(0o755)
            if expected is None:
                expected = hashlib.sha256(readback).hexdigest()
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{fake_bin}:{env['PATH']}",
                    "MC_STAT_JSON": stat_json if isinstance(stat_json, str) else json.dumps(stat_json),
                    "MC_RETENTION_JSON": retention_json if isinstance(retention_json, str) else json.dumps(retention_json),
                    "MC_READBACK_FILE": str(source),
                    "MC_CALLS": str(calls),
                }
            )
            result = subprocess.run(
                ["bash", str(SCRIPT), "worm", "bucket/object", expected, str(evidence)],
                cwd=BASE,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            result.calls = calls.read_text() if calls.exists() else ""  # type: ignore[attr-defined]
            result.evidence = json.loads(evidence.read_text()) if evidence.exists() else None  # type: ignore[attr-defined]
            return result

    def success_stat(self) -> dict[str, str]:
        return {
            "status": "success",
            "versionID": "test-version",
            "urlpath": "worm/bucket/object",
        }

    def success_retention(self) -> dict[str, str]:
        return json.loads(SUCCESS_FIXTURE.read_text(encoding="utf-8"))

    def test_status_success_mode_compliance_passes(self):
        result = self.run_verifier(stat_json=self.success_stat(), retention_json=self.success_retention())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.evidence["retention_status"], "success")
        self.assertEqual(result.evidence["retention_mode"], "COMPLIANCE")
        self.assertTrue(result.evidence["hash_match"])
        self.assertTrue(result.evidence["retention_verified"])

    def test_status_success_mode_governance_fails(self):
        retention = self.success_retention()
        retention["mode"] = "GOVERNANCE"
        result = self.run_verifier(stat_json=self.success_stat(), retention_json=retention)
        self.assertNotEqual(result.returncode, 0)

    def test_status_success_empty_mode_fails(self):
        retention = self.success_retention()
        retention["mode"] = ""
        result = self.run_verifier(stat_json=self.success_stat(), retention_json=retention)
        self.assertNotEqual(result.returncode, 0)

    def test_failure_status_fails(self):
        retention = self.success_retention()
        retention["status"] = "failure"
        result = self.run_verifier(stat_json=self.success_stat(), retention_json=retention)
        self.assertNotEqual(result.returncode, 0)

    def test_missing_mode_fails(self):
        retention = self.success_retention()
        del retention["mode"]
        result = self.run_verifier(stat_json=self.success_stat(), retention_json=retention)
        self.assertNotEqual(result.returncode, 0)

    def test_missing_version_id_fails_closed(self):
        stat = self.success_stat()
        del stat["versionID"]
        result = self.run_verifier(stat_json=stat, retention_json=self.success_retention())
        self.assertNotEqual(result.returncode, 0)

    def test_past_until_fails(self):
        retention = self.success_retention()
        retention["until"] = "2000-01-01T00:00:00Z"
        result = self.run_verifier(stat_json=self.success_stat(), retention_json=retention)
        self.assertNotEqual(result.returncode, 0)

    def test_hash_mismatch_fails(self):
        result = self.run_verifier(
            stat_json=self.success_stat(),
            retention_json=self.success_retention(),
            expected="0" * 64,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_malformed_json_fails_closed(self):
        result = self.run_verifier(stat_json="{not-json", retention_json=self.success_retention())
        self.assertNotEqual(result.returncode, 0)

    def test_readback_uses_exact_version_id(self):
        result = self.run_verifier(stat_json=self.success_stat(), retention_json=self.success_retention())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("retention info --json --version-id test-version", result.calls)
        self.assertIn("cp --version-id test-version", result.calls)
        self.assertTrue(result.evidence["exact_version_read_back"])

    def test_status_mode_fallback_would_select_success_not_mode(self):
        data = self.success_retention()
        legacy_value = data.get("status") or data.get("mode")
        self.assertEqual(legacy_value, "success")
        self.assertNotEqual(legacy_value, "COMPLIANCE")


if __name__ == "__main__":
    unittest.main()
