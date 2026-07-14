from __future__ import annotations
from dataclasses import replace
from .hashing import sha256_object
from .models import Certification, Metric, Status, ValidatorResult, to_dict

REQUIRED = {"STRUCTURAL", "INFORMATION", "NUMERIC", "NAMED_ENTITY", "SEMANTIC", "GOVERNANCE", "ADVERSARIAL"}

def certify(generator_id: str, certifier_id: str, results: list[ValidatorResult], metrics: dict) -> Certification:
    failures: list[str] = []
    warnings: list[str] = []
    if generator_id == certifier_id:
        failures.append("CERTIFIER_INDEPENDENCE_NOT_PROVEN")
    present = {r.validator_type for r in results}
    if not REQUIRED.issubset(present):
        failures.append("REQUIRED_VALIDATOR_MISSING")
    if any(r.status == Status.FAIL for r in results):
        failures.append("VALIDATOR_FAILURE_PRESENT")
    for name in ("IRR", "NIR", "NEIR"):
        metric = metrics[name]
        if metric.status != Status.NOT_APPLICABLE and (metric.numerator != metric.denominator):
            failures.append(f"{name}_BELOW_100")
    if metrics["UAC"].value > 0:
        failures.append("UNSUPPORTED_ADDITION_DETECTED")
    if metrics["semantic_drift_count"] > 0:
        failures.append("SEMANTIC_DRIFT_DETECTED")
    if metrics["S4_failure_count"] > 0:
        failures.append("S4_FAILURE_PRESENT")
    if any(r.status in {Status.WARNING, Status.UNKNOWN, Status.REVIEW} for r in results):
        warnings.append("NON_BLOCKING_OR_UNRESOLVED_FINDINGS")
    if failures:
        cert = Certification(Status.FAIL, "NOT_CERTIFIED", tuple(sorted(set(failures))), tuple(warnings), "")
    elif warnings:
        cert = Certification(Status.REVIEW, "NOT_CERTIFIED", (), tuple(warnings), "")
    else:
        cert = Certification(Status.PASS, "CERTIFIED", (), (), "")
    return replace(cert, decision_hash=sha256_object(to_dict(cert)))
