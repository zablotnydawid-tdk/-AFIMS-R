from __future__ import annotations

from typing import Any

from .hashing import sha256_object


QUESTION_TEXT = {
    1: "Czy zachowano pełną intencję autora?",
    2: "Czy zachowano wszystkie fakty?",
    3: "Czy zachowano wszystkie liczby?",
    4: "Czy zachowano wszystkie nazwy?",
    5: "Czy zachowano wszystkie zależności?",
    6: "Czy zachowano wszystkie argumenty?",
    7: "Czy zachowano wszystkie wnioski?",
    8: "Czy zachowano stopień pewności?",
    9: "Czy oddzielono fakty od hipotez?",
    10: "Czy nie dodano niepotwierdzonych informacji?",
    11: "Czy każda zmiana jest możliwa do uzasadnienia?",
    12: "Czy przeprowadzono wszystkie wymagane testy?",
    13: "Czy nie wystąpił żaden krytyczny błąd?",
    14: "Czy istnieje jeszcze obiektywna poprawka zwiększająca jakość bez utraty informacji?",
}


def evaluate_final_confidence(compliance_report: dict[str, Any], case_results: list[dict[str, Any]]) -> dict[str, Any]:
    groups = compliance_report["groups"]
    summary = compliance_report["summary"]
    group_pass = lambda group: groups[group]["decision"] == "PASS"
    evidence_complete = all(
        item.get("evidence_hash_valid") is True
        and item.get("execution_status") == "PASS"
        and item.get("suite_expectation_met") is True
        for item in case_results
    )

    answers: dict[int, bool] = {
        1: group_pass("T1"),
        2: group_pass("T2"),
        3: group_pass("T2"),
        4: group_pass("T2"),
        5: group_pass("T3"),
        6: group_pass("T1") and group_pass("T2"),
        7: group_pass("T3") and group_pass("T7"),
        8: group_pass("T3"),
        9: group_pass("T5") and group_pass("T7"),
        10: group_pass("T5") and group_pass("T9") and group_pass("T10"),
        11: evidence_complete,
        12: summary["executed"] == 85 and summary["complete_fixtures"] == 85,
        13: summary["failed"] == 0 and summary["unresolved"] == 0,
    }
    required_case_fields = {
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
    improvement_audit_findings: list[str] = []
    ids = [item.get("test_id") for item in case_results]
    if len(ids) != 85 or len(set(ids)) != 85:
        improvement_audit_findings.append("CASE_SET_NOT_EXACTLY_85_UNIQUE_IDS")
    if any(required_case_fields - set(item) for item in case_results):
        improvement_audit_findings.append("CASE_CONTRACT_FIELD_MISSING")
    if set(groups) != {f"T{number}" for number in range(1, 11)}:
        improvement_audit_findings.append("GROUP_COVERAGE_NOT_T1_TO_T10")
    if not evidence_complete:
        improvement_audit_findings.append("EVIDENCE_OR_EXECUTION_IMPROVEMENT_REQUIRED")
    if not all(answers.values()):
        improvement_audit_findings.append("FINAL_CONFIDENCE_QUESTION_1_TO_13_FAILED")
    objective_improvement_remaining = bool(improvement_audit_findings)
    items = [
        {
            "question_number": number,
            "question": QUESTION_TEXT[number],
            "expected_answer": "YES",
            "observed_answer": "YES" if answers[number] else "NO",
            "passed": answers[number],
        }
        for number in range(1, 14)
    ]
    items.append(
        {
            "question_number": 14,
            "question": QUESTION_TEXT[14],
            "expected_answer": "NO",
            "observed_answer": "YES" if objective_improvement_remaining else "NO",
            "passed": not objective_improvement_remaining,
            "scope_qualifier": "within_declared_executable_reference_fixture_scope",
        }
    )
    decision = "PASS" if all(item["passed"] for item in items) else "FAIL"
    report = {
        "schema_version": "AFIMS-T.FinalConfidence.v1",
        "system": "AFIMS-R",
        "version": "0.4.0",
        "decision": decision,
        "questions": items,
        "tests_1_to_13_all_yes": all(answers.values()),
        "test_14_no": not objective_improvement_remaining,
        "test_14_method": {
            "name": "bounded_deterministic_fixture_completeness_audit",
            "findings": improvement_audit_findings,
            "exhaustive_outside_declared_scope": False,
        },
        "scope": "exact AFIMS-T executable reference fixture pack",
        "external_certification": False,
    }
    report["report_sha256"] = sha256_object(report)
    return report
