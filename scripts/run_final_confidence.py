from __future__ import annotations

import json
from pathlib import Path

from afims_r.final_confidence import evaluate_final_confidence


BASE = Path(__file__).resolve().parents[1]


def main() -> int:
    report = json.loads((BASE / "reports" / "AFIMS_T_COMPLIANCE_REPORT.json").read_text(encoding="utf-8"))
    results = json.loads((BASE / "reports" / "AFIMS_T_CASE_RESULTS.json").read_text(encoding="utf-8"))["results"]
    confidence = evaluate_final_confidence(report, results)
    output = BASE / "reports" / "FINAL_CONFIDENCE_REPORT.json"
    output.write_text(json.dumps(confidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("FINAL_CONFIDENCE_TESTS_1_TO_13: " + ("PASS" if confidence["tests_1_to_13_all_yes"] else "FAIL"))
    print("FINAL_CONFIDENCE_TEST_14: " + ("NO" if confidence["test_14_no"] else "YES"))
    print("FINAL_CONFIDENCE_DECISION: " + confidence["decision"])
    return 0 if confidence["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

