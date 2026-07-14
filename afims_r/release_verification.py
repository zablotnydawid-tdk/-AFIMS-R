from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def verify_release_evidence(
    base: Path,
    report: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    failures: list[str] = []
    artifacts = manifest.get("artifacts", [])
    for artifact in artifacts:
        test_id = artifact.get("test_id", "UNKNOWN")
        path = base / artifact.get("path", "")
        if not path.is_file():
            failures.append(f"missing:{test_id}")
        elif sha256(path) != artifact.get("sha256"):
            failures.append(f"hash:{test_id}")

    summary = report.get("summary", {})
    expected = {
        "complete_fixtures": 85,
        "executed": 85,
        "passed": 85,
        "failed": 0,
        "unresolved": 0,
        "valid_evidence": 85,
        "invalid_evidence_hashes": 0,
    }
    for field, value in expected.items():
        if summary.get(field) != value:
            failures.append(f"summary:{field}:{summary.get(field)!r}!={value!r}")
    if len(artifacts) != 85:
        failures.append(f"artifact_count:{len(artifacts)}!=85")
    if report.get("certification", {}).get("decision") != "PASS":
        failures.append("certifier_not_pass")

    return {
        "decision": "PASS" if not failures else "FAIL",
        "evidence_files_checked": len(artifacts),
        "failures": failures,
    }
