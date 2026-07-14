from __future__ import annotations
from .extraction import InformationModel
from .models import Metric, Status, ValidatorResult

def _rate(total: int, bad: int) -> Metric:
    if total == 0:
        return Metric(None, None, None, Status.NOT_APPLICABLE)
    good = max(0, total - bad)
    value = 100.0 * good / total
    return Metric(value, good, total, Status.PASS if bad == 0 else Status.FAIL)

def calculate(source: InformationModel, results: list[ValidatorResult]) -> dict:
    findings = [f for r in results for f in r.findings]
    numeric_bad = sum(1 for f in findings if f.category == "NUMERIC")
    entity_bad = sum(1 for f in findings if f.category == "ENTITY")
    semantic_bad = sum(1 for f in findings if f.category in {"NEGATION", "MODALITY"})
    info_bad = sum(1 for f in findings if f.category == "INFORMATION")
    s4 = sum(1 for f in findings if f.severity.value == "S4")
    return {
        "IRR": _rate(len(source.sentences), info_bad),
        "NIR": _rate(len(source.numbers), numeric_bad),
        "NEIR": _rate(len(source.entities), entity_bad),
        "SIS": _rate(max(1, len(source.sentences)), semantic_bad),
        "UAC": Metric(sum(1 for f in findings if f.rule_id in {"RG-102"}), None, None,
                      Status.PASS if not any(f.rule_id == "RG-102" for f in findings) else Status.FAIL),
        "semantic_drift_count": semantic_bad,
        "S4_failure_count": s4,
    }
