from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from .hashing import sha256_object


COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def build_readiness(
    compliance_report: dict[str, Any],
    final_confidence: dict[str, Any],
    release_verification_passed: bool,
) -> dict[str, Any]:
    local_gates = {
        "AFIMS-T-85": compliance_report["certification"]["decision"],
        "FINAL-CONFIDENCE-14": final_confidence["decision"],
        "RELEASE-MANIFEST": "PASS" if release_verification_passed else "FAIL",
    }
    local_pass = all(value == "PASS" for value in local_gates.values())
    report = {
        "schema_version": "AFIMS-R.ReleaseReadiness.v1",
        "system": "AFIMS-R",
        "version": "0.4.0",
        "local_evidence_decision": "PASS" if local_pass else "FAIL",
        "release_status": "READY_FOR_CI" if local_pass else "BLOCKED",
        "local_gates": local_gates,
        "external_gates": {
            "RG-026": "NOT_EXECUTED",
            "MINIO_WORM_UPLOAD": "NOT_EXECUTED",
            "MINIO_READBACK": "NOT_EXECUTED",
            "RG-027": "NOT_EXECUTED",
            "OPA_FINAL_CERTIFICATION": "NOT_EXECUTED",
            "COSIGN_SIGNATURE": "NOT_EXECUTED",
        },
        "governance_maturity": "NONE",
        "l3_granted": False,
        "l4_granted": False,
        "reason": "L3/L4 require execution of the external two-phase Release Governance v3.2 pipeline.",
    }
    report["report_sha256"] = sha256_object(report)
    return report


def build_ci_pipeline_input(
    repository: str,
    commit_sha: str,
    image_reference: str,
    image_digest: str,
    evidence_refs: dict[str, str],
) -> dict[str, Any]:
    if repository.count("/") != 1:
        raise ValueError("repository must use owner/name form")
    if not COMMIT_RE.fullmatch(commit_sha):
        raise ValueError("commit_sha must be a real 40-character lowercase hexadecimal Git commit")
    if not DIGEST_RE.fullmatch(image_digest):
        raise ValueError("image_digest must be sha256:<64 lowercase hex>")
    required_refs = {"afims_t", "final_confidence", "release_manifest", "tests"}
    if not required_refs.issubset(evidence_refs):
        raise ValueError(f"missing evidence refs: {sorted(required_refs - evidence_refs.keys())}")

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    gates = [
        {
            "id": gate_id,
            "mandatory": True,
            "severity": "CRITICAL",
            "status": "PASS",
            "evidence_ref": evidence_refs[key],
        }
        for gate_id, key in (
            ("AFIMS-T-85", "afims_t"),
            ("FINAL-CONFIDENCE-14", "final_confidence"),
            ("RELEASE-MANIFEST", "release_manifest"),
            ("tests", "tests"),
        )
    ]
    return {
        "schema_version": "3.2",
        "record_status": "PIPELINE_INPUT",
        "record_id": f"afims-r-{commit_sha[:12]}",
        "generated_at": now,
        "subject": {
            "repository": repository,
            "commit_sha": commit_sha,
            "image": {"reference": image_reference, "digest": image_digest},
        },
        "release_gates": gates,
        "operational_evidence": [],
        "evidence_graph": {
            "nodes": [
                {"id": "source", "type": "source"},
                {"id": "afims-t", "type": "test"},
                {"id": "final-confidence", "type": "test"},
                {"id": "image", "type": "artifact"},
                {"id": "archive", "type": "immutable_archive"},
                {"id": "decision", "type": "decision"},
            ],
            "edges": [
                {"from": "source", "to": "afims-t"},
                {"from": "afims-t", "to": "final-confidence"},
                {"from": "final-confidence", "to": "image"},
                {"from": "image", "to": "archive"},
                {"from": "archive", "to": "decision"},
            ],
        },
        "integrity": {"signed": False, "signature_verified": False},
        "claimed": {},
    }

