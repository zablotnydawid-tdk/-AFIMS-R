from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .hashing import sha256_object


@dataclass(frozen=True)
class SuiteCertification:
    decision: str
    reason_codes: tuple[str, ...]
    payload: dict[str, Any]


class IndependentSuiteCertifier:
    identity = "afims-independent-suite-certifier-v0.4.0"

    def certify(
        self,
        suite_manifest: dict[str, Any],
        results: list[dict[str, Any]],
        evidence_manifest: dict[str, Any],
    ) -> SuiteCertification:
        reasons: list[str] = []
        expected_count = suite_manifest["expected_case_count"]
        expected_ids = set(suite_manifest["case_ids"])
        result_ids = {item["test_id"] for item in results}
        actors = suite_manifest["actors"]

        if len(results) != expected_count or result_ids != expected_ids:
            reasons.append("INCOMPLETE_CASE_EXECUTION")
        if actors["generator"] == self.identity:
            reasons.append("GENERATOR_SELF_CERTIFICATION")
        if actors["validator"] == self.identity:
            reasons.append("VALIDATOR_CERTIFIER_COLLISION")
        if len(set(actors.values())) != len(actors):
            reasons.append("ROLE_SEPARATION_VIOLATION")
        if any(not item.get("suite_expectation_met", False) for item in results):
            reasons.append("TEST_EXPECTATION_FAILURE")
        if any(item.get("unresolved", 0) for item in results):
            reasons.append("UNRESOLVED_FINDING")
        if evidence_manifest.get("valid_evidence_count") != expected_count:
            reasons.append("EVIDENCE_INCOMPLETE")
        if evidence_manifest.get("invalid_hash_count") != 0:
            reasons.append("EVIDENCE_HASH_INVALID")

        decision = "FAIL" if reasons else "PASS"
        payload = {
            "system": "AFIMS-R",
            "version": "0.4.0",
            "scope": "AFIMS-T executable reference fixture conformance",
            "decision": decision,
            "reason_codes": reasons or ["ALL_CERTIFICATION_GATES_PASSED"],
            "suite_manifest_sha256": sha256_object(suite_manifest),
            "results_sha256": sha256_object(results),
            "evidence_manifest_sha256": sha256_object(evidence_manifest),
            "certifier_identity": self.identity,
            "external_certification": False,
        }
        payload["certificate_sha256"] = sha256_object(payload)
        return SuiteCertification(decision, tuple(payload["reason_codes"]), payload)
