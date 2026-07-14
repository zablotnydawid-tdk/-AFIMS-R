from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from afims_r.fixture_evaluator import evaluate_fixture
from afims_r.hashing import sha256_object
from afims_r.suite_certifier import IndependentSuiteCertifier


BASE = Path(__file__).resolve().parents[1]
REQUIRED_FIXTURE_FIELDS = {
    "test_id",
    "requirement",
    "severity",
    "input",
    "instruction",
    "expected_result",
    "prohibited_result",
    "evaluation_method",
    "executable_evaluator",
    "pass_criteria",
    "fail_criteria",
    "execution_status",
    "execution_timestamp",
    "observed_result",
    "evidence_artifact",
    "evidence_sha256",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_fixture_contract(cases: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for case in cases:
        missing = REQUIRED_FIXTURE_FIELDS - case.keys()
        if missing:
            failures.append(f"{case.get('test_id', '<unknown>')}: missing {sorted(missing)}")
        evaluator = case.get("executable_evaluator", {})
        if not evaluator.get("checks"):
            failures.append(f"{case.get('test_id', '<unknown>')}: no executable checks")
    return failures


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# AFIMS-T EXECUTABLE CONFORMANCE REPORT",
        "",
        f"- System: `{report['system']}`",
        f"- Version: `{report['version']}`",
        f"- Executed at: `{report['executed_at']}`",
        f"- Fixture contract: `{report['fixture_contract']}`",
        f"- Cases executed: `{report['summary']['executed']}/85`",
        f"- Suite expectations met: `{report['summary']['passed']}/85`",
        f"- Suite expectations failed: `{report['summary']['failed']}`",
        f"- Evidence valid: `{report['summary']['valid_evidence']}/85`",
        f"- Certifier: `{report['certification']['certifier_identity']}`",
        f"- Decision: **{report['certification']['decision']}**",
        "",
        "## Group results",
        "",
        "| Group | Executed | Passed | Failed | Decision |",
        "|---|---:|---:|---:|---|",
    ]
    for group, result in report["groups"].items():
        lines.append(
            f"| {group} | {result['executed']} | {result['passed']} | {result['failed']} | {result['decision']} |"
        )
    lines.extend(
        [
            "",
            "## Evidence boundary",
            "",
            "This PASS covers the executable reference fixture pack included in this exact release. ",
            "It is not external certification and does not prove universal hallucination detection or production-domain accuracy.",
            "",
            "## Final verdict",
            "",
            f"`FULL AFIMS-T EXECUTABLE FIXTURE COMPLIANCE: {report['certification']['decision']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    suite_path = BASE / "fixtures" / "afims_t_cases.json"
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    cases = suite["cases"]
    fixture_failures = validate_fixture_contract(cases)
    if fixture_failures:
        raise RuntimeError("Fixture contract invalid:\n" + "\n".join(fixture_failures))

    timestamp = datetime.now(timezone.utc).isoformat()
    evidence_dir = BASE / "evidence" / "afims_t"
    reports_dir = BASE / "reports"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    valid_evidence = 0
    invalid_hash_count = 0

    for case in cases:
        evaluation = evaluate_fixture(case)
        evidence = {
            "schema_version": "AFIMS-T.CaseEvidence.v1",
            "system": "AFIMS-R",
            "version": "0.4.0",
            "test_id": case["test_id"],
            "group": case["group"],
            "executed_at": timestamp,
            "fixture_sha256": case["fixture_sha256"],
            "input_sha256": sha256_object({"content": case["input"]}),
            "candidate_sha256": sha256_object({"content": case["candidate_output"]}),
            "evaluation": evaluation,
        }
        evidence_path = evidence_dir / f"{case['test_id'].replace('.', '_')}.json"
        write_json(evidence_path, evidence)
        evidence_hash = file_sha256(evidence_path)
        observed_hash = file_sha256(evidence_path)
        hash_valid = evidence_hash == observed_hash
        valid_evidence += int(hash_valid)
        invalid_hash_count += int(not hash_valid)

        result = dict(case)
        result.update(
            {
                "execution_status": "PASS" if evaluation["suite_expectation_met"] and hash_valid else "FAIL",
                "execution_timestamp": timestamp,
                "observed_result": evaluation,
                "evidence_artifact": str(evidence_path.relative_to(BASE)),
                "evidence_sha256": evidence_hash,
                "evidence_hash_valid": hash_valid,
                "suite_expectation_met": evaluation["suite_expectation_met"] and hash_valid,
                "unresolved": evaluation["unresolved"],
            }
        )
        results.append(result)

    write_json(reports_dir / "AFIMS_T_CASE_RESULTS.json", {"case_count": len(results), "results": results})

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        grouped[result["group"]].append(result)

    group_summary: dict[str, Any] = {}
    for group in sorted(grouped, key=lambda value: int(value[1:])):
        items = grouped[group]
        passed = sum(1 for item in items if item["suite_expectation_met"])
        group_report = {
            "schema_version": "AFIMS-T.GroupReport.v1",
            "group": group,
            "executed_at": timestamp,
            "executed": len(items),
            "passed": passed,
            "failed": len(items) - passed,
            "decision": "PASS" if passed == len(items) else "FAIL",
            "case_results": [
                {
                    "test_id": item["test_id"],
                    "execution_status": item["execution_status"],
                    "evidence_artifact": item["evidence_artifact"],
                    "evidence_sha256": item["evidence_sha256"],
                }
                for item in items
            ],
        }
        write_json(reports_dir / "groups" / f"{group}_REPORT.json", group_report)
        group_summary[group] = {key: group_report[key] for key in ("executed", "passed", "failed", "decision")}

    evidence_manifest = {
        "schema_version": "AFIMS-T.EvidenceManifest.v1",
        "expected_evidence_count": 85,
        "valid_evidence_count": valid_evidence,
        "invalid_hash_count": invalid_hash_count,
        "artifacts": [
            {
                "test_id": result["test_id"],
                "path": result["evidence_artifact"],
                "sha256": result["evidence_sha256"],
            }
            for result in results
        ],
    }
    write_json(BASE / "evidence" / "EVIDENCE_MANIFEST.json", evidence_manifest)

    suite_manifest = {
        "system": "AFIMS-R",
        "version": "0.4.0",
        "expected_case_count": 85,
        "case_ids": [case["test_id"] for case in cases],
        "group_distribution": dict(Counter(case["group"] for case in cases)),
        "actors": {
            "generator": "afims-fixture-generator-v0.4.0",
            "validator": "afims-fixture-validator-v0.4.0",
            "certifier": "afims-independent-suite-certifier-v0.4.0",
        },
        "fixtures_sha256": file_sha256(suite_path),
    }
    write_json(reports_dir / "SUITE_MANIFEST.json", suite_manifest)

    certification = IndependentSuiteCertifier().certify(suite_manifest, results, evidence_manifest)
    write_json(reports_dir / "CERTIFICATE.json", certification.payload)

    passed = sum(1 for item in results if item["suite_expectation_met"])
    report = {
        "schema_version": "AFIMS-T.ComplianceReport.v1",
        "system": "AFIMS-R",
        "version": "0.4.0",
        "executed_at": timestamp,
        "fixture_contract": "COMPLETE" if not fixture_failures else "INVALID",
        "summary": {
            "mapped": 85,
            "complete_fixtures": len(cases),
            "executed": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "unresolved": sum(item["unresolved"] for item in results),
            "valid_evidence": valid_evidence,
            "invalid_evidence_hashes": invalid_hash_count,
        },
        "groups": group_summary,
        "certification": certification.payload,
        "declaration_boundary": {
            "reference_fixture_conformance": certification.decision,
            "external_certification": "NOT_CLAIMED",
            "production_domain_validation": "NOT_PROVEN",
            "universal_hallucination_detection": "NOT_CLAIMED",
        },
    }
    report["report_sha256"] = sha256_object(report)
    write_json(reports_dir / "AFIMS_T_COMPLIANCE_REPORT.json", report)
    (reports_dir / "AFIMS_T_COMPLIANCE_REPORT.md").write_text(markdown_report(report), encoding="utf-8")

    print(f"FIXTURES_COMPLETE: {len(cases)}/85")
    print(f"CASES_EXECUTED: {len(results)}/85")
    print(f"SUITE_EXPECTATIONS_MET: {passed}/85")
    print(f"EVIDENCE_VALID: {valid_evidence}/85")
    print(f"CERTIFIER_DECISION: {certification.decision}")
    return 0 if certification.decision == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
