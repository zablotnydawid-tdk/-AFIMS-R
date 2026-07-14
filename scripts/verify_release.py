from __future__ import annotations

import json
from pathlib import Path

from afims_r.release_verification import verify_release_evidence


BASE = Path(__file__).resolve().parents[1]


def main() -> int:
    report = json.loads((BASE / "reports" / "AFIMS_T_COMPLIANCE_REPORT.json").read_text(encoding="utf-8"))
    manifest = json.loads((BASE / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
    result = verify_release_evidence(BASE, report, manifest)
    print(f"EVIDENCE_FILES_CHECKED: {result['evidence_files_checked']}")
    print(f"VERIFICATION_FAILURES: {len(result['failures'])}")
    for failure in result["failures"]:
        print(f"FAIL: {failure}")
    print("RELEASE_VERIFICATION: " + result["decision"])
    return 0 if result["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
