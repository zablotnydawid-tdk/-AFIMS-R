from __future__ import annotations

import argparse
import json
from pathlib import Path

from afims_r.governance_adapter import build_ci_pipeline_input


BASE = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--image-reference", required=True)
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--output", default="release-input.afims-r.json")
    args = parser.parse_args()
    data = build_ci_pipeline_input(
        repository=args.repository,
        commit_sha=args.commit_sha,
        image_reference=args.image_reference,
        image_digest=args.image_digest,
        evidence_refs={
            "afims_t": "reports/AFIMS_T_COMPLIANCE_REPORT.json",
            "final_confidence": "reports/FINAL_CONFIDENCE_REPORT.json",
            "release_manifest": "RELEASE_MANIFEST.json",
            "tests": "evidence/tests.log",
        },
    )
    output = BASE / args.output
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

