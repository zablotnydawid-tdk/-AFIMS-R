from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

class Status(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    REVIEW = "REVIEW"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class Severity(str, Enum):
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"

@dataclass(frozen=True)
class Finding:
    finding_id: str
    validator_id: str
    rule_id: str
    severity: Severity
    category: str
    explanation: str
    blocking: bool = False
    source_locator: str | None = None
    answer_locator: str | None = None
    expected: Any = None
    observed: Any = None
    evidence_refs: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class Metric:
    value: float | int | None
    numerator: int | None
    denominator: int | None
    status: Status

@dataclass(frozen=True)
class ValidatorResult:
    validator_id: str
    validator_type: str
    version: str
    status: Status
    findings: tuple[Finding, ...] = ()
    result_hash: str = ""

@dataclass(frozen=True)
class Certification:
    verdict: Status
    certification_status: str
    failures: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    decision_hash: str = ""

def to_dict(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, tuple):
        return [to_dict(v) for v in obj]
    if isinstance(obj, list):
        return [to_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj
