from __future__ import annotations

import json
from pathlib import Path

from afims_r.governance_adapter import build_readiness
from afims_r.release_verification import verify_release_evidence


BASE = Path(__file__).resolve().parents[1]


def main() -> int:
    compliance = json.loads((BASE / "reports" / "AFIMS_T_COMPLIANCE_REPORT.json").read_text(encoding="utf-8"))
    confidence = json.loads((BASE / "reports" / "FINAL_CONFIDENCE_REPORT.json").read_text(encoding="utf-8"))
    manifest = json.loads((BASE / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
    verification = verify_release_evidence(BASE, compliance, manifest)
    readiness = build_readiness(compliance, confidence, verification["decision"] == "PASS")
    readiness["release_verification"] = verification
    output = BASE / "reports" / "RELEASE_READINESS.json"
    output.write_text(json.dumps(readiness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("LOCAL_EVIDENCE_DECISION: " + readiness["local_evidence_decision"])
    print("RELEASE_STATUS: " + readiness["release_status"])
    print("GOVERNANCE_MATURITY: " + readiness["governance_maturity"])
    return 0 if readiness["release_status"] == "READY_FOR_CI" else 1


if __name__ == "__main__":
    raise SystemExit(main())
